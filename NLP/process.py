#!/usr/bin/env python3
import argparse
import datetime
import logging
import json
import pymysql
import time
from collections import Counter
from nlp_main_handler import NLPMH
from helper import init_logging

dolphin = None


def main():
    global dolphin
    init_logging("process")
    args = parse_arguments()
    dolphin = get_dolphin(args)
    end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")
    start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
    # Get date slices.
    date_slices = list()
    date_slices.extend(get_date_slices(start_date, end_date, 3))
    date_slices.extend(get_date_slices(start_date, end_date, 7))
    date_slices.extend(get_date_slices(start_date, end_date, 15))
    logging.info("Get %s slices.", len(date_slices))
    # Get reviews.
    reviews = get_reviews(date_slices, dolphin)
    # Process.
    for batch in reviews:
        result = {
            "window_length": batch["slice"]["window_length"],
            "window_end_date": batch["slice"]["end_date"],
            "appid": batch["app"]
        }
        logging.info(
            "Processing app [%s] [%s] [%s]",
            batch["app"],
            batch["slice"]["end_date"],
            batch["slice"]["window_length"]
        )
        if check_batch(batch["app"], batch["slice"]):
            logging.info("Record exists.")
            continue
        batch_num = 5
        while True:
            try:
                n = NLPMH(batch["reviews"]["positive"], args.api_key, batch_num)
            except Exception as e:
                logging.error("Failed to request API: ", e)
                continue
            else:
                break
        positive = parse(n.result)
        while True:
            try:
                n = NLPMH(batch["reviews"]["negative"], args.api_key, batch_num)
            except Exception as e:
                logging.error("Failed to request API: ", e)
                continue
            else:
                break
        negative = parse(n.result)
        result["top_up_tags"] = positive["keywords"]
        result["top_down_tags"] = negative["keywords"]
        result["top_up_sentences"] = positive["phrase"]
        result["top_down_sentences"] = negative["phrase"]
        result["top_up_reviews"], result["top_down_reviews"] = \
            get_top_reviews(batch["app"], batch["slice"])
        result["emotion"] = dict(Counter(positive["emotion"]) + Counter(negative["emotion"]))
        save(result)


def save(result):
    for k in result:
        result[k] = json.dumps(result[k])
    sql = "INSERT INTO `results`" \
          "(`appid`, " \
          "`window_length`, " \
          "`window_end_date`, " \
          "`top_up_tags`, " \
          "`top_down_tags`, " \
          "`top_up_sentences`, " \
          "`top_down_sentences`, " \
          "`top_up_reviews`, " \
          "`top_down_reviews`, " \
          "`emotion`) " \
          "VALUES " \
          "( %(appid)s, " \
          "%(window_length)s, " \
          "str_to_date(" + result["window_end_date"] + ", '%%Y-%%m-%%d'), " \
          "%(top_up_tags)s, " \
          "%(top_down_tags)s, " \
          "%(top_up_sentences)s, " \
          "%(top_down_sentences)s, " \
          "%(top_up_reviews)s, " \
          "%(top_down_reviews)s, " \
          "%(emotion)s) "
    with dolphin.cursor() as cursor:
        cursor.execute(sql, result)


def parse(results):
    parsed = dict()
    if results["emotion"]["code"] != 200:
        parsed["emotion"] = {results["emotion"]["code"]: 1}
    else:
        parsed["emotion"] = results["emotion"]["emotion"]["probabilities"]
    if results["phrase"]["code"] != 200:
        parsed["phrase"] = {results["phrase"]["code"]: 1}
    else:
        parsed["phrase"] = {
            x["keyword"]: x["relevance_score"]
            for x in results["phrase"]["keywords"]
        }
    if results["keywords"]["code"] != 200:
        parsed["keywords"] = {results["keywords"]["code"]: 1}
    else:
        parsed["keywords"] = {
            x["keyword"]: x["confidence_score"]
            for x in results["keywords"]["keywords"]
        }
    return parsed


def get_top_reviews(app, slice):
    sql = "SELECT " \
          "`recommendationid`, " \
          "(users.weight + reviews.weight * 2) as weight2 " \
          "FROM `reviews`, `users`" + \
          "where " \
          "reviews.weight > 0 " \
          "and users.weight > 0 " \
          "and reviews.steamid = users.steamid " \
          "and reviews.edited_at > %s " \
          "and reviews.edited_at < %s " \
          "and reviews.appid = %s " \
          "and reviews.type = %s " \
          "and reviews.language = 'english' " \
          "order by weight2 desc " \
          "limit 8"""
    with dolphin.cursor() as cursor:
        cursor.execute(
            sql,
            (
                slice["start_time"],
                slice["end_time"],
                app,
                "positive"
            )
        )
        ups = cursor.fetchall()
        cursor.execute(
            sql,
            (
                slice["start_time"],
                slice["end_time"],
                app,
                "negative"
            )
        )
        downs = cursor.fetchall()
    return {x["recommendationid"]: x["weight2"] for x in ups}, \
           {x["recommendationid"]: x["weight2"] for x in downs}


def check_batch(app, slice):
    sql = "SELECT * " \
          "FROM `results` " \
          "WHERE `window_length` = %s AND `window_end_date` = %s AND `appid` = %s"
    with dolphin.cursor() as cursor:
        cursor.execute(
            sql,
            (
                slice["window_length"],
                slice["end_date"],
                app
            )
        )
        if cursor.fetchone():
            return True
        else:
            return False


def get_reviews(date_slices, dolphin):
    apps = list(map(lambda x: x["appid"], get_apps()))
    reviews = list()
    for app in apps:
        for s in date_slices:
            if check_batch(app, s):
                continue
            sql = """
                select 
                reviews.appid,
                reviews.recommendationid, 
                reviews.content, 
                reviews.`language`, 
                reviews.weight as review_weight, 
                users.weight as user_weight,
                (users.weight + reviews.weight * 2) as weight2,
                reviews.type
                from 
                reviews, 
                users 
                where 
                reviews.weight > 0 
                and users.weight > 0 
                and reviews.steamid = users.steamid 
                and reviews.edited_at > %s
                and reviews.edited_at < %s
                and reviews.appid = %s
                and reviews.type = %s
                and reviews.language = 'english'
                order by weight2 desc 
                limit 100
                """
            with dolphin.cursor() as cursor:
                cursor.execute(sql, (
                    s["start_time"],
                    s["end_time"],
                    app,
                    'positive'
                ))
                positive_results = cursor.fetchall()
                cursor.execute(sql, (
                    s["start_time"],
                    s["end_time"],
                    app,
                    'negative'
                ))
                negative_results = cursor.fetchall()
            reviews.append({
                "app": app,
                "slice": s,
                "reviews": {
                    "positive": positive_results,
                    "negative": negative_results
                }
            })
    return reviews


def get_date_slices(start_date, end_date, window_length):
    date_slices = []
    new_end = end_date
    while new_end - datetime.timedelta(days=window_length) >= start_date:
        new_start = new_end - datetime.timedelta(days=window_length)
        date_slices.append(
            {
                "start_time": int(time.mktime(new_start.timetuple())),
                "end_time": int(time.mktime(new_end.timetuple())),
                "window_length": window_length,
                "end_date": new_end.strftime('%Y-%m-%d'),
            }
        )
        new_end -= datetime.timedelta(days=1)
    return date_slices


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


def get_apps():
    """
    Get apps with their "last_crawled".
    :param dolphin:
    :return:
    """
    query_sql = "SELECT `appid` FROM `apps` WHERE `is_concerned` = 1"
    with dolphin.cursor() as cursor:
        cursor.execute(query_sql)
        results = cursor.fetchall()
    return results


def parse_arguments():
    """
    Parse arguments from command line and return the results.
    :return: parsed args
    """
    parser = argparse.ArgumentParser(description="PB NLP Tool.")
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
    parser.add_argument("-s", "--start-date", action="store", dest="start_date",
                        required=True, help="Start date")
    parser.add_argument("-e", "--end-date", action="store", dest="end_date",
                        required=True, help="End date")
    parser.add_argument("-k", "--api-key", action="store", dest="api_key",
                        required=True, help="API key of paralleldots.")
    return parser.parse_args()


if __name__ == "__main__":
    main()
