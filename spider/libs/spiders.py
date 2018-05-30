import logging
import json
import requests
import time
import pika


class UserSpider(object):
    pass


class GameSpider(object):
    """
    This class craws metadata of games.
    """
    API_URL = "https://store.steampowered.com/api/appdetails"
    API_PARAMS = {
        "format": "json",
        "l": "en"
    }

    def __init__(self, appid, channel, method, pub_channel):
        self.appid = appid
        self.channel = channel
        self.method = method
        self.pub_channel = pub_channel
        self.api_params = self.API_PARAMS
        self.api_params["appids"] = appid

    def crawl(self):
        while True:
            # Try to request API.
            try:
                api_raw_result = requests.get(
                    url=self.API_URL,
                    params=self.api_params
                )
            except Exception as e:
                logging.error("Failed to request API: %s", e)
                time.sleep(5)
                continue
            # Try to parse the result as JSON.
            try:
                api_result = api_raw_result.json()[str(self.appid)]
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
                game = {
                    "appid": self.appid,
                    "name": api_result["data"]["name"],
                    "labels": [x["description"] for x in api_result["data"]["categories"]],
                    "types": [x["description"] for x in api_result["data"]["genres"]],
                    "image": api_result["data"]["header_image"],
                    "is_concerned": 0,
                    "crawled_at": 0
                }
                # Save the results.
                self.pub_channel.basic_publish(
                    exchange="ubi",
                    routing_key="game.result",
                    body=json.dumps(game),
                    properties=pika.BasicProperties(delivery_mode=2,)
                )
            except KeyError as e:
                logging.error("Incorrect result format: %s", e)
                logging.error("API cannot handle requests now.")
                time.sleep(10)
                continue
            # If reaching here, the query is successful.
            break


class ReviewSpider(object):
    """
    This class crawls reviews and send ACK after finishing.
    """
    API_URL = "https://store.steampowered.com/appreviews/{}"
    API_PARAMS = {
        "json": 1,
        "filter": "updated",
        "start_offset": 0,
    }

    def __init__(self, appid, last_updated, language, channel, method, pub_channel):
        self.appid = appid
        self.last_updated = last_updated
        self.language = language
        self.channel = channel
        self.method = method
        self.pub_channel = pub_channel
        self.api_params = self.API_PARAMS
        self.api_params["language"] = language
        self.api_url = self.API_URL.format(appid)

    def crawl(self):
        while True:
            # Try to request API.
            try:
                api_raw_result = requests.get(
                    url=self.api_url,
                    params=self.api_params
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
                logging.error("API cannot handle requests now.")
                time.sleep(10)
                continue
            # If reaching here, the query is successful.
            self.api_params["start_offset"] += api_result["query_summary"]["num_reviews"]
            logging.info("Crawled %d reviews so far.", self.api_params["start_offset"])
        logging.info("Crawl finished after getting %d reviews.", self.api_params["start_offset"])

    def _save(self, reviews):
        for review in reviews:
            if review["timestamp_updated"] < self.last_updated:
                # We have reached the "last_updated"
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
                "games": [],                # as default value
                "review_count": review["author"]["num_reviews"],
                "screenshot_count": 0,      # as default value
                "workshop_item_count": 0,   # as default value
                "badge_count": 0,           # as default value
                "group_count": 0,           # as default value
                "game_count": review["author"]["num_games_owned"],
                "friend_count": 0,          # as default value
                "registered_at": 0          # as default value
            }
            self.pub_channel.basic_publish(
                exchange="ubi",
                routing_key="user.order.pre",
                body=json.dumps(parsed_user),
                properties=pika.BasicProperties(delivery_mode=2,)
            )
            self.pub_channel.basic_publish(
                exchange="ubi",
                routing_key="review.result",
                body=json.dumps(parsed_review),
                properties=pika.BasicProperties(delivery_mode=2,)
            )
        return False
