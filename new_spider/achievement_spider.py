#!/usr/bin/env python3
import argparse
import json
import logging
import pymysql
import queue
import requests
import threading
import time
from functools import reduce
from helper import init_logging


class AchievementSpider(object):
    """
    This class crawls games.
    """
    API_URL = "http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
    API_PARAMS = {
        "key": "78460B6C7D432BD39D71B0CE60939B14"
    }

    def __init__(self, review, dolphin):
        self.review = review
        self.dolphin = dolphin
        self.api_params = self.API_PARAMS.copy()
        self.api_params["steamid"] = review["steamid"]
        self.api_params["appid"] = review["appid"]
        self.recommendationid = review["recommendationid"]

    def crawl(self):
        while True:
            logging.info("Crawling review [%d]:[%d]", self.review["appid"], self.review["steamid"])
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
                api_result = api_raw_result.json()["playerstats"]
            except Exception as e:
                logging.error("Failed to interpreter API result as JSON: %s", e)
                time.sleep(5)
                continue
            # Try to parse and save the results.
            try:
                if not api_result["success"]:
                    # API query failed.
                    logging.error("This user's achievement data is not public.")
                    ratio = 0
                else:
                    ratio = reduce(lambda x, y: x + y, map(lambda x: x["achieved"], api_result["achievements"]))\
                            / len(api_result["achievements"])
                # Save the results.
                logging.info("The ratio is " + str(ratio))
                self._save(ratio)
            except KeyError as e:
                logging.error("Incorrect result format: %s", e)
                time.sleep(10)
                continue
            # If reaching here, the query is successful.
            logging.info("Crawl finished.")
            break

    def _save(self, ratio):
        create_sql = "UPDATE `ubi`.`reviews` SET `achievement_ratio` = %s " \
                     "WHERE `recommendationid` = %s"
        with self.dolphin.cursor() as cursor:
            cursor.execute(create_sql, (ratio, self.recommendationid))


def spider_booster(review_queue, args):
    """
    This function start a spider to crawl games.
    :param review_queue:
    :param args:
    :return:
    """
    dolphin = get_dolphin(args)
    while not review_queue.empty():
        # Try to get a game ID non-blocking.
        try:
            review = review_queue.get(False)
        except queue.Empty:
            dolphin.close()
            return
        spider = AchievementSpider(review, dolphin)
        spider.crawl()
    dolphin.close()


def main():
    # Initialise.
    args = parse_arguments()
    init_logging("achievement")
    dolphin = get_dolphin(args)
    # Get reviews to crawl.
    logging.info("Getting reviews...")
    reviews = get_steamids_and_appids(dolphin)
    dolphin.close()
    # Set up a queue.
    review_queue = queue.Queue()
    for review in reviews:
        review_queue.put(review)
    # Start many threads to crawl reviews.
    logging.info("Starting %d threads...", args.thread)
    threads = []
    for i in range(0, args.thread):
        thread = threading.Thread(
            target=spider_booster,
            name="Spider" + str(i),
            args=(review_queue, args)
        )
        threads.append(thread)
        thread.start()
    # Wait for all threads to finish.
    for thread in threads:
        thread.join()


def get_steamids_and_appids(dolphin):
    """
    Get users' games .
    :param dolphin:
    :return:
    """
    query_sql = "SELECT `recommendationid`, `steamid`, `appid` FROM `reviews` " \
                "WHERE `reviews`.`achievement_ratio` IS NULL AND " \
                "EXISTS(SELECT * FROM `apps` WHERE `appid` = `reviews`.`appid` " \
                "AND `with_achievement` = 1);"
    # Query all users' games.
    with dolphin.cursor() as cursor:
        cursor.execute(query_sql)
        results = cursor.fetchall()
    # Merge all lists without duplication.
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
    parser = argparse.ArgumentParser(description="PB Achievement Spider.")
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
