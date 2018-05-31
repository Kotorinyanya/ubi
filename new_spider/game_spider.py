#!/usr/bin/env python3
import argparse
import json
import logging
import pymysql
import queue
import requests
import threading
import time
from helper import init_logging


class GameSpider(object):
    """
    This class crawls games.
    """
    API_URL = "https://store.steampowered.com/api/appdetails"
    API_PARAMS = {
        "format": "json",
        "l": "en"
    }

    def __init__(self, appid, dolphin):
        self.appid = appid
        self.dolphin = dolphin
        self.api_params = self.API_PARAMS.copy()
        self.api_params["appids"] = appid

    def crawl(self):
        if self._has_game(self.appid):
            # Already exists, no need to crawl.
            return
        while True:
            logging.info("Crawling app [%d]", self.appid)
            # Try to request API.
            try:
                api_raw_result = requests.get(
                    url=self.API_URL,
                    params=self.api_params,
                    timeout=10
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
                    logging.error("API cannot handle requests now, or this game doesn't exist.")
                    return
                game = {
                    "appid": self.appid,
                    "name": api_result["data"]["name"],
                    "labels": json.dumps(
                        [x["description"] for x in api_result["data"]["categories"]]
                        if "categories" in api_result["data"]
                        else []
                    ),
                    "types": json.dumps(
                        [x["description"] for x in api_result["data"]["genres"]]
                        if "genres" in api_result["data"]
                        else []
                    ),
                    "image": api_result["data"]["header_image"],
                    "is_concerned": 0,
                    "crawled_at": 0
                }
                # Save the results.
                self._save(game)
            except KeyError as e:
                logging.error("Incorrect result format: %s", e)
                time.sleep(10)
                continue
            # If reaching here, the query is successful.
            logging.info("Crawl finished.")
            break

    def _save(self, game):
        create_sql = "INSERT INTO `apps` (`appid`, `name`, `labels`," \
                     "`types`, `image`, `is_concerned`, `crawled_at`) VALUES" \
                     "(%(appid)s, %(name)s, %(labels)s," \
                     "%(types)s, %(image)s, %(is_concerned)s, %(crawled_at)s)"
        with self.dolphin.cursor() as cursor:
            cursor.execute(create_sql, game)

    def _has_game(self, appid):
        """
        Check if a game already exists in the database.
        :param appid:
        :return:
        """
        query_sql = "SELECT `appid` FROM `apps` where `appid` = %s"
        with self.dolphin.cursor() as cursor:
            cursor.execute(query_sql, (appid,))
            result = cursor.fetchone()
        if result:
            return True
        else:
            return False


def spider_booster(game_queue, args):
    """
    This function start a spider to crawl games.
    :param game_queue:
    :param args:
    :return:
    """
    dolphin = get_dolphin(args)
    while not game_queue.empty():
        # Try to get a game ID non-blocking.
        try:
            game_id = game_queue.get(False)
        except queue.Empty:
            dolphin.close()
            return
        spider = GameSpider(game_id, dolphin)
        spider.crawl()
    dolphin.close()


def main():
    # Initialise.
    args = parse_arguments()
    init_logging("game")
    dolphin = get_dolphin(args)
    # Get games to crawl.
    logging.info("Getting games...")
    games = get_games(dolphin)
    dolphin.close()
    # Set up a queue.
    game_queue = queue.Queue()
    for game in games:
        game_queue.put(game)
    # Start many threads to crawl games.
    logging.info("Starting %d threads...", args.thread)
    threads = []
    for i in range(0, args.thread):
        thread = threading.Thread(
            target=spider_booster,
            name="Spider" + str(i),
            args=(game_queue, args)
        )
        threads.append(thread)
        thread.start()
    # Wait for all threads to finish.
    for thread in threads:
        thread.join()


def get_games(dolphin):
    """
    Get users' games.
    :param dolphin:
    :return:
    """
    query_sql = "SELECT `games` FROM `users`"
    result_list = list()
    # Query all users' games.
    with dolphin.cursor() as cursor:
        cursor.execute(query_sql)
        results = cursor.fetchall()
    # Merge all lists without duplication.
    for result in results:
        result_list.extend(
            [
                x for x in json.loads(result["games"]) if x not in result_list
            ]
        )
    return result_list


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
    parser.add_argument("--thread", action="store", default=5, type=int,
                        help="Specify threads of this spider.")
    return parser.parse_args()


if __name__ == "__main__":
    main()
