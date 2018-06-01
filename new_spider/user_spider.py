#!/usr/bin/env python3
import argparse
import datetime
import json
import logging
import pymysql
import queue
import re
import requests
import threading
import time
from bs4 import BeautifulSoup
from helper import init_logging


class UserSpider(object):
    """
    This class crawls games.
    """
    API_KEY = "2B29AEA2D769011AA4D4D1AFF45AB7FE"
    API_PARAMS = {
        "key": API_KEY,
        "format": "json"
    }
    SUMMARY_API_URL = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    OWNED_GAMES_API_URL = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    LEVEL_API_URL = "http://api.steampowered.com/IPlayerService/GetSteamLevel/v1/"
    COMMUNITY_URL = "https://steamcommunity.com/profiles/"

    def __init__(self, steamid, dolphin):
        self.steamid = steamid
        self.dolphin = dolphin
        self.summary_api_params = self.API_PARAMS.copy()
        self.summary_api_params["steamids"] = steamid
        self.owned_games_api_params = self.API_PARAMS.copy()
        self.owned_games_api_params["steamid"] = steamid
        self.level_api_params = self.API_PARAMS.copy()
        self.level_api_params["steamid"] = steamid
        self.user = {
            "steamid": steamid,
            "nickname": "",
            "avatar": "",
            "country": "",
            "level": 0,
            "games": [],
            "dlc_count": 0,
            "screenshot_count": 0,
            "workshop_item_count": 0,
            "badge_count": 0,
            "group_count": 0,
            "friend_count": 0,
            "registered_at": 0
        }

    def crawl(self):
        logging.info("Crawling user [%d]", self.steamid)
        # Try to request API.
        self._crawl_summary_api()
        self._crawl_owned_games_api()
        self._crawl_level_api()
        self._crawl_community()
        # If reaching here, the query is successful.
        self._save()
        logging.info("Crawl finished.")

    def _crawl_community(self):
        url = self.COMMUNITY_URL + str(self.steamid)
        while True:
            # Try to request the page.
            try:
                raw_result = requests.get(url=url, timeout=10)
                break
            except Exception as e:
                logging.error("Failed to request community: %s", e)
                time.sleep(5)
                continue
        pattern = re.compile('.*?total">(.*?)</span>', re.S)
        soup = BeautifulSoup(raw_result.text, 'lxml')
        dlc = soup.select('.gamecollector_showcase .value')
        dlc1 = "0"
        if dlc:
            dlc1 = soup.select('.gamecollector_showcase .value')[1].get_text().\
                replace('\t','').replace('\n', '').replace('\r', '')
        badges = "0"
        ach = soup.select('.profile_count_link_preview_ctn .profile_count_link_total')
        if ach:
            badges = soup.select('.profile_count_link_preview_ctn .profile_count_link_total')[0].get_text()
        sel2 = soup.find_all(href=re.compile('/screenshots/'))
        screenshots = "0"
        if sel2:
            screenshots = sel2
            screenshots = re.findall(pattern, str(screenshots))[0]
        workshop_item = "0"
        sel3 = soup.find_all(href=re.compile('/myworkshopfiles/'))
        if sel3:
            workshop_item = sel3
            workshop_item = re.findall(pattern, str(workshop_item))[0]
        friend_count = "0"
        sel4 = soup.find_all(href=re.compile('/friends/'))
        if sel4:
            friend_count = sel4
            friend_count = re.findall(pattern, str(friend_count))[0]
        group_count = "0"
        sel5 = soup.find_all(href=re.compile('/groups/'))
        if sel5:
            group_count = sel5
            group_count = re.findall(pattern, str(group_count))[0]
        self.user["dlc_count"] = int(dlc1.replace(',', ''))
        self.user["badge_count"] = int(badges.replace(',', ''))
        self.user["screenshot_count"] = int(screenshots.replace(',', ''))
        self.user["workshop_item_count"] = int(workshop_item.replace(',', ''))
        self.user["friend_count"] = int(friend_count.replace(',', ''))
        self.user["group_count"] = int(group_count.replace(',', ''))

    def _crawl_level_api(self):
        while True:
            # Try to request API.
            try:
                api_raw_result = requests.get(
                    url=self.LEVEL_API_URL,
                    params=self.level_api_params,
                    timeout=10
                )
            except Exception as e:
                logging.error("Failed to request API: %s", e)
                time.sleep(5)
                continue
            # Try to parse the result as JSON.
            try:
                api_result = api_raw_result.json()["response"]["player_level"]
            except KeyError:
                logging.warning("Cannot get this user's level.")
                break
            except Exception as e:
                logging.error("Failed to interpreter API result as JSON: %s", e)
                time.sleep(5)
                continue
            # Try to parse and save the results.
            try:
                self.user["level"] = api_result
            except KeyError as e:
                logging.error("Incorrect result format: %s", e)
                time.sleep(10)
                continue
            # If reaching here, the query is successful.
            break

    def _crawl_owned_games_api(self):
        while True:
            # Try to request API.
            try:
                api_raw_result = requests.get(
                    url=self.OWNED_GAMES_API_URL,
                    params=self.owned_games_api_params,
                    timeout=10
                )
            except Exception as e:
                logging.error("Failed to request API: %s", e)
                time.sleep(5)
                continue
            # Try to parse the result as JSON.
            try:
                api_result = api_raw_result.json()["response"]["games"]
            except KeyError:
                logging.warning("Cannot get this user's games.")
                break
            except Exception as e:
                logging.error("Failed to interpreter API result as JSON: %s", e)
                time.sleep(5)
                continue
            # Try to parse and save the results.
            try:
                self.user["games"] = [x["appid"] for x in api_result]
            except KeyError as e:
                logging.error("Incorrect result format: %s", e)
                time.sleep(10)
                continue
            # If reaching here, the query is successful.
            break

    def _crawl_summary_api(self):
        while True:
            # Try to request API.
            try:
                api_raw_result = requests.get(
                    url=self.SUMMARY_API_URL,
                    params=self.summary_api_params,
                    timeout=10
                )
            except Exception as e:
                logging.error("Failed to request API: %s", e)
                time.sleep(5)
                continue
            # Try to parse the result as JSON.
            try:
                api_result = api_raw_result.json()["response"]["players"][0]
            except Exception as e:
                logging.error("Failed to interpreter API result as JSON: %s", e)
                time.sleep(5)
                continue
            # Try to parse and save the results.
            try:
                self.user["nickname"] = \
                    api_result["personaname"] if "personaname" in api_result else "?"
                self.user["avatar"] = \
                    api_result["avatarfull"] if "avatarfull" in api_result else ""
                self.user["registered_at"] =\
                    api_result["timecreated"] if "timecreated" in api_result else 0
                self.user["country"] =\
                    api_result["loccountrycode"] if "loccountrycode" in api_result else ""
            except KeyError as e:
                logging.error("Incorrect result format: %s", e)
                time.sleep(10)
                continue
            # If reaching here, the query is successful.
            break

    def _save(self):
        self.user["games"] = json.dumps(self.user["games"])
        update_sql = "UPDATE `users` SET " \
                     "`nickname` = %(nickname)s," \
                     "`avatar` = %(avatar)s," \
                     "`country` = %(country)s," \
                     "`level` = %(level)s," \
                     "`games` = %(games)s," \
                     "`dlc_count` = %(dlc_count)s," \
                     "`screenshot_count` = %(screenshot_count)s," \
                     "`workshop_item_count` = %(workshop_item_count)s," \
                     "`badge_count` = %(badge_count)s," \
                     "`group_count` = %(group_count)s," \
                     "`friend_count` = %(friend_count)s," \
                     "`registered_at` = %(registered_at)s " \
                     "WHERE `steamid` = %(steamid)s"
        with self.dolphin.cursor() as cursor:
            cursor.execute(update_sql, self.user)


def spider_booster(user_queue, args):
    """
    This function start a spider to crawl games.
    :param user_queue:
    :param args:
    :return:
    """
    dolphin = get_dolphin(args)
    while not user_queue.empty():
        # Try to get a game ID non-blocking.
        try:
            user_id = user_queue.get(False)
        except queue.Empty:
            dolphin.close()
            return
        spider = UserSpider(user_id, dolphin)
        spider.crawl()
    dolphin.close()


def main():
    # Initialise.
    args = parse_arguments()
    init_logging("user")
    dolphin = get_dolphin(args)
    # Get users to crawl.
    logging.info("Getting users...")
    users = get_users(dolphin, args.interval)
    dolphin.close()
    # Set up a queue.
    user_queue = queue.Queue()
    for user in users:
        user_queue.put(user)
    # Start many threads to crawl games.
    logging.info("Starting %d threads...", args.thread)
    threads = []
    for i in range(0, args.thread):
        thread = threading.Thread(
            target=spider_booster,
            name="Spider" + str(i),
            args=(user_queue, args)
        )
        threads.append(thread)
        thread.start()
    # Wait for all threads to finish.
    for thread in threads:
        thread.join()


def get_users(dolphin, interval):
    """
    Get users' games.
    :param dolphin:
    :param interval:
    :return:
    """
    timestamp = int(time.time()) - interval
    date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    query_sql = "SELECT `steamid` FROM `users` WHERE `nickname` = '' or `updated_at` < %s"
    # Query all users' games.
    with dolphin.cursor() as cursor:
        cursor.execute(query_sql, (date,))
        results = cursor.fetchall()
    # Get Steam ID list.
    return [x["steamid"] for x in results]


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
    parser.add_argument("--interval", action="store", default=3600 * 24 * 7, type=int,
                        help="Specify time before user data expires.")
    return parser.parse_args()


if __name__ == "__main__":
    main()
