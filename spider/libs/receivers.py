import datetime
import logging
import json
import time
import pika


class GameOrderReceiver(object):
    """
    This class checks if a game should be crawled.
    If so, the order will be issued.
    """
    def __init__(self, dolphin, pub_channel, order):
        self.dolphin = dolphin
        self.pub_channel = pub_channel
        self.order = order

    def issue(self):
        query_sql = "SELECT * FROM `apps` WHERE `appid` = %s"
        with self.dolphin.cursor() as cursor:
            cursor.execute(query_sql, (self.order["appid"],))
            game = cursor.fetchone()
        if game:
            # The game already exists.
            logging.info("App [%s] already exists, not crawling.", str(self.order["appid"]))
            return
        # The order should be issued.
        self.pub_channel.basic_publish(
            exchange="ubi",
            routing_key="game.order",
            body=json.dumps(self.order),
            properties=pika.BasicProperties(delivery_mode=2,)
        )


class UserOrderReceiver(object):
    """
    This class checks if a user should be crawled.
    If so, the order will be issued.
    """
    def __init__(self, dolphin, pub_channel, order, expire_time):
        self.dolphin = dolphin
        self.pub_channel = pub_channel
        self.order = order
        self.expire_time = expire_time

    def issue(self):
        query_sql = "SELECT * FROM `users` WHERE `steamid` = %s"
        with self.dolphin.cursor() as cursor:
            cursor.execute(query_sql, (self.order["steamid"],))
            user = cursor.fetchone()
        if user and user["updated_at"] - time.time() < self.expire_time:
            # The user's data is too new to update.
            logging.info("User [%s] doesn't need an update, not crawling.", str(self.order["steamid"]))
            return
        elif user:
            self.order["update"] = True
        # The order should be issued.
        self.pub_channel.basic_publish(
            exchange="ubi",
            routing_key="user.order",
            body=json.dumps(self.order),
            properties=pika.BasicProperties(delivery_mode=2,)
        )


class ReviewReceiver(object):
    """
    This class saves reviews results, and make statistics.
    """
    def __init__(self, dolphin, review):
        self.dolphin = dolphin
        self.review = review
        self.old = self._get_old_review()

    def add_stat(self):
        review_date = datetime.datetime.fromtimestamp(
            self.review["edited_at"]
        ).strftime('%Y-%m-%d')
        query_sql = "SELECT COUNT(*) FROM `review_changes` " \
                    "WHERE `appid`=%s AND date=str_to_date(%s, '%%Y-%%m-%%d')"
        with self.dolphin.cursor() as cursor:
            cursor.execute(query_sql, (self.review["appid"], review_date))
            count = cursor.fetchone()["COUNT(*)"]
        if not count:
            # The record need to be created.
            with self.dolphin.cursor() as cursor:
                create_sql = "INSERT INTO `review_changes` (`appid`, `date`) VALUES (%s, str_to_date(%s,'%%Y-%%m-%%d'))"
                cursor.execute(create_sql, (self.review["appid"], review_date))
        if self.old and self.review["type"] == self.old["type"]:
            # The review exists before, and the type hasn't be changed.
            return
        # At here, either it's a new review, or its type is changed.
        if self.review["type"] == "positive":
            if self.old:
                update_sql = "UPDATE `review_changes` SET `down_to_up` = `down_to_up`+1 WHERE `appid` = %s AND" \
                             "`date`=str_to_date(%s, '%%Y-%%m-%%d')"
            else:
                update_sql = "UPDATE `review_changes` SET `new_up` = `new_up`+1 WHERE `appid` = %s AND" \
                             "`date`=str_to_date(%s, '%%Y-%%m-%%d')"
        else:
            if self.old:
                update_sql = "UPDATE `review_changes` SET `up_to_down` = `up_to_down`+1 WHERE `appid` = %s AND" \
                             "`date`=str_to_date(%s, '%%Y-%%m-%%d')"
            else:
                update_sql = "UPDATE `review_changes` SET `new_down` = `new_down`+1 WHERE `appid` = %s AND" \
                             "`date`=str_to_date(%s, '%%Y-%%m-%%d')"
        with self.dolphin.cursor() as cursor:
            cursor.execute(update_sql, (self.review["appid"], review_date))
        self.dolphin.commit()

    def save(self):
        if self.old:
            sql = "UPDATE `reviews` SET" \
                  "`playtime_forever` = %(playtime_forever)s," \
                  "`playtime_last_two_weeks` = %(playtime_last_two_weeks)s," \
                  "`last_played` = %(last_played)s," \
                  "`language` = %(language)s," \
                  "`content` = %(content)s," \
                  "`steam_weight` = %(steam_weight)s," \
                  "`weight` = %(weight)s," \
                  "`type` = %(type)s," \
                  "`vote_up_count` = %(vote_up_count)s," \
                  "`vote_funny_count` = %(vote_funny_count)s," \
                  "`comment_count` = %(comment_count)s," \
                  "`published_at` = %(published_at)s," \
                  "`edited_at` = %(edited_at)s " \
                  "WHERE `recommendationid` = %(recommendationid)s"
        else:
            sql = "INSERT INTO `reviews` (`recommendationid`, `appid`, `steamid`," \
                  "`playtime_forever`, `playtime_last_two_weeks`, `last_played`," \
                  "`language`, `content`, `steam_weight`, `weight`, `type`," \
                  "`vote_up_count`, `vote_funny_count`, `comment_count`," \
                  "`published_at`, `edited_at`) VALUES" \
                  "(%(recommendationid)s, %(appid)s, %(steamid)s," \
                  "%(playtime_forever)s, %(playtime_last_two_weeks)s," \
                  "%(last_played)s, %(language)s, %(content)s, %(steam_weight)s," \
                  "%(weight)s, %(type)s, %(vote_up_count)s, %(vote_funny_count)s," \
                  "%(comment_count)s, %(published_at)s, %(edited_at)s)"
        with self.dolphin.cursor() as cursor:
            cursor.execute(sql, self.review)
        self.dolphin.commit()

    def _get_old_review(self):
        """
        This function query if this review has been saved before.
        :return:
        """
        recommendation_id = self.review["recommendationid"]
        query_sql = "SELECT * FROM `reviews` WHERE `recommendationid` = %s"
        with self.dolphin.cursor() as cursor:
            # Query apps haven't be crawled in some time.
            cursor.execute(query_sql, (recommendation_id,))
            result = cursor.fetchone()
        return result


class UserReceiver(object):
    """
    This class saves reviews results, and make statistics.
    """
    def __init__(self, dolphin, user):
        self.dolphin = dolphin
        self.user = user
        self.user["games"] = json.dumps(self.user["games"])

    def save(self):
        if "update" in self.user.keys():
            sql = "UPDATE `users` SET" \
                  "`nickname` = %(nickname)s," \
                  "`avatar` = %(avatar)s," \
                  "`country` = %(country)s," \
                  "`level` = %(level)s," \
                  "`games` = %(games)s," \
                  "`review_count` = %(review_count)s," \
                  "`screenshot_count` = %(screenshot_count)s," \
                  "`workshop_item_count` = %(workshop_item_count)s," \
                  "`badge_count` = %(badge_count)s," \
                  "`group_count` = %(group_count)s," \
                  "`game_count` = %(game_count)s," \
                  "`friend_count` = %(friend_count)s," \
                  "`registered_at` = %(registered_at)s " \
                  "WHERE `steamid` = %(steamid)s"
        else:
            sql = "INSERT INTO `users` (`steamid`, `nickname`, `avatar`," \
                  "`country`, `level`, `games`," \
                  "`review_count`, `screenshot_count`, `workshop_item_count`," \
                  "`badge_count`, `group_count`," \
                  "`game_count`, `friend_count`, `registered_at`) VALUES" \
                  "(%(steamid)s, %(nickname)s, %(avatar)s," \
                  "%(country)s, %(level)s, %(games)s, %(review_count)s," \
                  "%(screenshot_count)s, %(workshop_item_count)s," \
                  "%(badge_count)s, %(group_count)s, %(game_count)s, %(friend_count)s," \
                  "%(registered_at)s)"
        with self.dolphin.cursor() as cursor:
            cursor.execute(sql, self.user)
        self.dolphin.commit()


class GameReceiver(object):
    """
    This class saves reviews results, and make statistics.
    """
    def __init__(self, dolphin, game):
        self.dolphin = dolphin
        self.game = game
        self.game["labels"] = json.dumps(self.game["labels"])
        self.game["types"] = json.dumps(self.game["types"])

    def save(self):
        create_sql = "INSERT INTO `apps` (`appid`, `name`, `labels`," \
              "`types`, `image`, `is_concerned`, `crawled_at`) VALUES" \
              "(%(appid)s, %(name)s, %(labels)s," \
              "%(types)s, %(image)s, %(is_concerned)s, %(crawled_at)s)"
        with self.dolphin.cursor() as cursor:
            cursor.execute(create_sql, self.game)
        self.dolphin.commit()
