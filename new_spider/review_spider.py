#!/usr/bin/env python3
import argparse
import datetime
import json
import logging
import pymysql
import requests
import threading
import time
from helper import init_logging


class ReviewSpider(object):
    """
    This class crawls reviews.
    """
    API_URL = "https://store.steampowered.com/appreviews/{}"
    API_PARAMS = {
        "json": 1,
        "filter": "updated",
        "start_offset": 0,
    }

    def __init__(self, appid, last_crawled, language, dolphin):
        self.appid = appid
        self.last_crawled = last_crawled
        self.language = language
        self.dolphin = dolphin
        self.api_params = self.API_PARAMS.copy()
        self.api_params["language"] = language
        self.api_url = self.API_URL.format(appid)

    def crawl(self, order=0, thread_num=1):
        self.api_params["start_offset"] = order * 20
        while True:
            logging.info(
                "Crawling %d~%d",
                self.api_params["start_offset"] + 1,
                self.api_params["start_offset"] + 20
            )
            # Try to request API.
            try:
                api_raw_result = requests.get(
                    url=self.api_url,
                    params=self.api_params,
                    timeout=10
                )
            except Exception as e:
                logging.error("Failed to request API: %s", e)
                time.sleep(5)
                continue
            # Try to parse the result as JSON.
            try:
                api_result = api_raw_result.json()
            except Exception as e:
                logging.error("Failed to interpreter API result as JSON: %s", e)
                time.sleep(5)
                continue
            # Try to parse and save the results.
            try:
                if not api_result["success"]:
                    # API query failed.
                    logging.error("API cannot handle requests now.")
                    time.sleep(10)
                    continue
                if not api_result["query_summary"]["num_reviews"]:
                    # No more reviews are available.
                    logging.info("No more reviews.")
                    break
                # Save the results.
                finished = self._save(api_result["reviews"])
                if finished:
                    # We have reached "last_updated"
                    logging.info("Reaching last timestamp.")
                    break
            except KeyError as e:
                logging.error("Incorrect result format: %s", e)
                time.sleep(10)
                continue
            # If reaching here, the query is successful.
            self.api_params["start_offset"] += 20 * thread_num
        logging.info("Crawl finished.")

    def _save(self, reviews):
        for review in reviews:
            if review["timestamp_updated"] < self.last_crawled:
                # We have reached the "last_crawled"
                return True
            parsed_review = {
                "recommendationid": review["recommendationid"],
                "appid": self.appid,
                "steamid": review["author"]["steamid"],
                "playtime_forever": review["author"]["playtime_forever"],
                "playtime_last_two_weeks": review["author"]["playtime_last_two_weeks"],
                "last_played": review["author"]["last_played"],
                "language": review["language"],
                "content": review["review"],
                "steam_weight": review["weighted_vote_score"],
                "weight": 0,                # as default value
                "type": "positive" if review["voted_up"] else "negative",
                "vote_up_count": review["votes_up"],
                "vote_funny_count": review["votes_funny"],
                "comment_count": review["comment_count"],
                "published_at": review["timestamp_created"],
                "edited_at": review["timestamp_updated"]
            }
            parsed_user = {
                "steamid": review["author"]["steamid"],
                "nickname": "",             # as default value
                "avatar": "",               # as default value
                "country": "",              # as default value
                "level": 0,                 # as default value
                "weight": 0,                # as default value
                "games": json.dumps([]),    # as default value
                "review_count": review["author"]["num_reviews"],
                "screenshot_count": 0,      # as default value
                "workshop_item_count": 0,   # as default value
                "badge_count": 0,           # as default value
                "group_count": 0,           # as default value
                "game_count": review["author"]["num_games_owned"],
                "friend_count": 0,          # as default value
                "registered_at": 0          # as default value
            }

            # Save a basic user if not already in.
            if not self._has_user(parsed_user["steamid"]):
                user_sql = "INSERT INTO `users` (`steamid`, `nickname`, `avatar`," \
                      "`country`, `level`, `games`," \
                      "`review_count`, `screenshot_count`, `workshop_item_count`," \
                      "`badge_count`, `group_count`," \
                      "`game_count`, `friend_count`, `registered_at`) VALUES" \
                      "(%(steamid)s, %(nickname)s, %(avatar)s," \
                      "%(country)s, %(level)s, %(games)s, %(review_count)s," \
                      "%(screenshot_count)s, %(workshop_item_count)s," \
                      "%(badge_count)s, %(group_count)s, %(game_count)s, %(friend_count)s," \
                      "%(registered_at)s)"
            else:
                user_sql = "UPDATE " \
                             "`users` " \
                             "SET " \
                             "`nickname` = %(steamid)s, " \
                             "`avatar` = %(avatar)s, " \
                             "`country` = %(country)s, " \
                             "`level` = %(level)s, " \
                             "`games` = %(games)s, " \
                             "`review_count` = %(review_count)s, " \
                             "`screenshot_count` = %(screenshot_count)s, " \
                             "`workshop_item_count` = %(workshop_item_count)s, " \
                             "`badge_count` = %(badge_count)s, " \
                             "`group_count` = %(group_count)s, " \
                             "`game_count` = %(game_count)s, " \
                             "`friend_count` = %(friend_count)s"
            with self.dolphin.cursor() as cursor:
                try:
                    cursor.execute(user_sql, parsed_user)
                except Exception as e:
                    logging.info(
                        "Failed to save user [%s]: %s",
                        str(review["author"]["steamid"]),
                        e
                    )

            # Save the review and do stat.
            review_date = datetime.datetime.fromtimestamp(parsed_review["edited_at"]).strftime('%Y-%m-%d')
            self._add_stat(self.appid, review_date)
            old_review_type = self._has_review(parsed_review["recommendationid"])
            if not old_review_type:
                # A new review
                create_sql = "INSERT INTO `reviews` (`recommendationid`, `appid`, `steamid`," \
                      "`playtime_forever`, `playtime_last_two_weeks`, `last_played`," \
                      "`language`, `content`, `steam_weight`, `weight`, `type`," \
                      "`vote_up_count`, `vote_funny_count`, `comment_count`," \
                      "`published_at`, `edited_at`) VALUES" \
                      "(%(recommendationid)s, %(appid)s, %(steamid)s," \
                      "%(playtime_forever)s, %(playtime_last_two_weeks)s," \
                      "%(last_played)s, %(language)s, %(content)s, %(steam_weight)s," \
                      "%(weight)s, %(type)s, %(vote_up_count)s, %(vote_funny_count)s," \
                      "%(comment_count)s, %(published_at)s, %(edited_at)s)"
                if parsed_review["type"] == "positive":
                    update_sql = "UPDATE `review_changes` SET `new_up` = `new_up`+1 WHERE `appid` = %s AND" \
                                 "`date`=str_to_date(%s, '%%Y-%%m-%%d')"
                else:
                    update_sql = "UPDATE `review_changes` SET `new_down` = `new_down`+1 WHERE `appid` = %s AND" \
                                 "`date`=str_to_date(%s, '%%Y-%%m-%%d')"
                with self.dolphin.cursor() as cursor:
                    cursor.execute(update_sql, (self.appid, review_date))
            else:
                # An update to an existing review.
                create_sql = "UPDATE `reviews` SET " \
                      "`playtime_forever` = %(playtime_forever)s, " \
                      "`playtime_last_two_weeks` = %(playtime_last_two_weeks)s, " \
                      "`last_played` = %(last_played)s, " \
                      "`language` = %(language)s, " \
                      "`content` = %(content)s, " \
                      "`steam_weight` = %(steam_weight)s, " \
                      "`weight` = %(weight)s, " \
                      "`type` = %(type)s, " \
                      "`vote_up_count` = %(vote_up_count)s, " \
                      "`vote_funny_count` = %(vote_funny_count)s, " \
                      "`comment_count` = %(comment_count)s, " \
                      "`published_at` = %(published_at)s, " \
                      "`edited_at` = %(edited_at)s " \
                      "WHERE `recommendationid` = %(recommendationid)s"
                if parsed_review["type"] != old_review_type:
                    if parsed_review["type"] == "positive":
                        update_sql = "UPDATE `review_changes` SET `down_to_up` = `down_to_up`+1 " \
                                     "WHERE `appid` = %s AND `date`=str_to_date(%s, '%%Y-%%m-%%d')"
                    else:
                        update_sql = "UPDATE `review_changes` SET `up_to_down` = `up_to_down`+1 " \
                                     "WHERE `appid` = %s AND `date`=str_to_date(%s, '%%Y-%%m-%%d')"
                    with self.dolphin.cursor() as cursor:
                        cursor.execute(update_sql, (self.appid, review_date))
            with self.dolphin.cursor() as cursor:
                try:
                    cursor.execute(create_sql, parsed_review)
                except Exception as e:
                    logging.info(
                        "Failed to save review [%s]: %s",
                        str(review["recommendationid"]),
                        e
                    )
        return False

    def _add_stat(self, appid, review_date):
        """
        Create stat of the day if not existing.
        :param appid:
        :param review_date:
        :return:
        """
        query_sql = "SELECT COUNT(*) FROM `review_changes` " \
                    "WHERE `appid`=%s AND date=str_to_date(%s, '%%Y-%%m-%%d')"
        with self.dolphin.cursor() as cursor:
            cursor.execute(query_sql, (appid, review_date))
            count = cursor.fetchone()["COUNT(*)"]
        if not count:
            # The record need to be created.
            with self.dolphin.cursor() as cursor:
                create_sql = "INSERT INTO `review_changes` (`appid`, `date`) VALUES (%s, str_to_date(%s,'%%Y-%%m-%%d'))"
                cursor.execute(create_sql, (appid, review_date))

    def _has_review(self, recommendationid):
        """
        Check if a review already exists in the database.
        :param recommendationid:
        :return:
        """
        query_sql = "SELECT `type` FROM `reviews` where `recommendationid` = %s"
        with self.dolphin.cursor() as cursor:
            cursor.execute(query_sql, (recommendationid,))
            result = cursor.fetchone()
        if result:
            return result["type"]
        else:
            return None

    def _has_user(self, steamid):
        """
        Check if a user already exists in the database.
        :param steamid:
        :return:
        """
        query_sql = "SELECT `steamid` FROM `users` where `steamid` = %s"
        with self.dolphin.cursor() as cursor:
            cursor.execute(query_sql, (steamid,))
            result = cursor.fetchone()
        if result:
            return True
        else:
            return False


def spider_booster(appid, last_crawled, language, order, thread_num, args):
    """
    This function start a spider to crawl reviews.
    :param appid:
    :param last_crawled:
    :param language:
    :param order:
    :param thread_num:
    :param args:
    :return:
    """
    logging.info(
        "Start crawling reviews of app [%d] since [%d] in [%s]",
        appid,
        last_crawled,
        language
    )
    dolphin = get_dolphin(args)
    spider = ReviewSpider(appid, last_crawled, language, dolphin)
    spider.crawl(order, thread_num)
    dolphin.close()


def main():
    # Initialise.
    args = parse_arguments()
    init_logging("review")
    dolphin = get_dolphin(args)
    start_time = int(time.time())
    # Get apps to crawl.
    apps = get_apps(dolphin)
    # Start crawling by each app.
    for app in apps:
        threads = []
        # Start threads for current app.
        for i in range(0, args.thread):
            thread = threading.Thread(
                target=spider_booster,
                name="Spider" + str(i),
                args=(
                    app["appid"],
                    app["crawled_at"],
                    args.review_language,
                    i,
                    args.thread,
                    args
                )
            )
            threads.append(thread)
            thread.start()
        # Wait for all threads to finish.
        for thread in threads:
            thread.join()
        # Update this app's "crawled_at"
        update_app(app["appid"], start_time, dolphin)
    dolphin.close()


def update_app(appid, start_time, dolphin):
    """
    Update "crawled_at" of an app.
    :param appid:
    :param start_time:
    :param dolphin:
    :return:
    """
    update_sql = "UPDATE `apps` SET `crawled_at` = %s WHERE `appid` = %s"
    with dolphin.cursor() as cursor:
        cursor.execute(update_sql, (start_time, appid))


def get_apps(dolphin):
    """
    Get apps with their "last_crawled".
    :param dolphin:
    :return:
    """
    query_sql = "SELECT `appid`, `crawled_at` FROM `apps` WHERE `is_concerned` = 1"
    with dolphin.cursor() as cursor:
        cursor.execute(query_sql)
        results = cursor.fetchall()
    return results


def get_dolphin(args):
    """
    Get an instance of pymysql for MySQL.
    :return:
    """
    dolphin = pymysql.connect(
        host=args.db_host,
        port=args.db_port,
        user=args.db_user,
        password=args.db_password,
        db=args.db_name,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
    return dolphin


def parse_arguments():
    """
    Parse arguments from command line and return the results.
    :return: parsed args
    """
    parser = argparse.ArgumentParser(description="PB Review Spider.")
    parser.add_argument("--debug", action="store_true",
                        help="Use this option to enable debug mode.")
    parser.add_argument("--mysql-host", action="store", dest="db_host",
                        default="localhost", help="Specify MySQL host address.")
    parser.add_argument("--mysql-port", action="store", dest="db_port",
                        default=3306, type=int, help="Specify MySQL host port.")
    parser.add_argument("--mysql-user", action="store", dest="db_user",
                        default="root", help="Specify MySQL user.")
    parser.add_argument("--mysql-password", action="store", dest="db_password",
                        default="root", help="Specify MySQL password.")
    parser.add_argument("--mysql-db", action="store", dest="db_name",
                        default="ubi", help="Specify MySQL database.")
    parser.add_argument("--language", action="store",
                        dest="review_language", default="all",
                        help="Specify reviews of what language to crawl.")
    parser.add_argument("--thread", action="store", default=5, type=int,
                        help="Specify threads of this spider.")
    return parser.parse_args()


if __name__ == "__main__":
    main()
