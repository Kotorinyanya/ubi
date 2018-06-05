#!/usr/bin/env python3
import argparse
import logging
import pymysql
from helper import init_logging
from helper import slicing
from predict_review_weight import PRW
from predic_player_weight import PPW


def main():
    # Initialise.
    args = parse_arguments()
    init_logging("weight")
    dolphin = get_dolphin(args)
    # Weight reviews.
    logging.info("Weighting reviews...")
    reviews = get_reviews(dolphin)
    weight_reviews(args, reviews)
    # Weight users.
    logging.info("Weighting users...")
    users = get_users(dolphin)
    weight_users(args, users)


def weight_users(args, users):
    # Calculate weights.
    results = dict()
    for these_users in slicing(users, 1000):
        ppw = PPW(these_users)
        weight_pairs = {
            x[0]: float(x[1])
            for x in zip(map(lambda x: x["steamid"], these_users), ppw.result)
        }
        results.update(weight_pairs)
    logging.info("Updating database...")
    update_sql = "UPDATE " \
                 "`users` " \
                 "SET " \
                 "`weight` = %s " \
                 "WHERE " \
                 "`steamid` = %s"
    dolphin = get_dolphin(args)
    for steamid, weight in results.items():
        with dolphin.cursor() as cursor:
            try:
                cursor.execute(update_sql, (weight, steamid))
            except Exception as e:
                logging.error("Failed to save user weight [%s]: %s", steamid, e)


def weight_reviews(args, reviews):
    update_sql = "UPDATE " \
                 "`reviews` " \
                 "SET " \
                 "`weight` = %s " \
                 "WHERE " \
                 "`recommendationid` = %s"
    # Calculate weights.
    for language, these_reviews in reviews.items():
        logging.info("Weighting reviews in [%s]", language)
        for result_slice in slicing(these_reviews, 300):
            # Process 1000 one time
            logging.info("Weighting a slice...")
            prw = PRW(result_slice)
            review_ids = [x["recommendationid"] for x in result_slice]
            review_weights = [x[0] for x in prw.weights]
            results = list(zip(review_ids, review_weights))
            logging.info("Updating database...")
            dolphin = get_dolphin(args)
            for result in results:
                with dolphin.cursor() as cursor:
                    try:
                        cursor.execute(update_sql, (float(result[1]), result[0]))
                    except Exception as e:
                        logging.error("Failed to save review weight [%s]: %s", result[0], e)
            dolphin.close()


def get_users(dolphin):
    query_sql = "select " \
                "steamid, " \
                "level, " \
                "review_count, " \
                "screenshot_count, " \
                "workshop_item_count, " \
                "badge_count, " \
                "group_count, " \
                "game_count, " \
                "dlc_count, " \
                "friend_count " \
                "FROM " \
                "users " \
                "where " \
                "EXISTS(" \
                    "select * " \
                    "from reviews " \
                    "where reviews.steamid = users.steamid " \
                    "and `language` in ('english', 'schinese', 'japanese', 'french') " \
                    "group by steamid);"
    # Query all reviews to weight.
    with dolphin.cursor() as cursor:
        cursor.execute(query_sql)
        results = cursor.fetchall()
    return results


def get_reviews(dolphin):
    query_sql = "SELECT " \
                "recommendationid, " \
                "content, " \
                "`language` " \
                "FROM " \
                "reviews " \
                "WHERE " \
                "`language` in ('english', 'schinese', 'japanese', 'french') " \
                "AND `weight` = 0"
    # Query all reviews to weight.
    with dolphin.cursor() as cursor:
        cursor.execute(query_sql)
        results = cursor.fetchall()
    # Classify by language.
    reviews = {
        "english": list(),
        "french": list(),
        "japanese": list(),
        "schinese": list()
    }
    for result in results:
        reviews[result["language"]].append(result)
    return reviews


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
    parser = argparse.ArgumentParser(description="PB Balance.")
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
    return parser.parse_args()


if __name__ == "__main__":
    main()
