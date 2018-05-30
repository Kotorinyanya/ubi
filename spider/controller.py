#!/usr/bin/env python3
import argparse
import logging
import json
import threading
import time
import pika
import pymysql
from libs.helper import init_logging
from libs.helper import init_rabbit
from libs.receivers import UserOrderReceiver
from libs.receivers import GameOrderReceiver
from libs.receivers import ReviewReceiver
from libs.receivers import UserReceiver
from libs.receivers import GameReceiver

args = None
user_spider_checker_pub_channel = None
game_spider_checker_pub_channel = None


def game_spider_checker_callback(channel, method, properties, body):
    """
    This function checks if a user should be crawled.
    :param channel:
    :param method:
    :param properties:
    :param body:
    :return:
    """
    try:
        game_order = GameOrderReceiver(
            get_dolphin(),
            game_spider_checker_pub_channel,
            json.loads(body)
        )
        game_order.issue()
    except Exception as e:
        logging.error("Failed to save review: %s", e)
    # Send ACK.
    channel.basic_ack(delivery_tag=method.delivery_tag)


def game_spider_checker():
    """
    This function checks if a user should be crawled.
    :return:
    """
    global game_spider_checker_pub_channel
    rabbit = get_rabbit()
    init_rabbit(rabbit)
    game_spider_checker_pub_channel = rabbit.channel()
    rabbit_channel = rabbit.channel()
    rabbit_channel.basic_qos(prefetch_count=1)
    rabbit_channel.basic_consume(
        game_spider_checker_callback,
        queue="game.order.pre"
    )
    rabbit_channel.start_consuming()


def game_result_receiver_callback(channel, method, properties, body):
    """
    This function gets user results and handle it with UserReceiver class.
    :param channel:
    :param method:
    :param properties:
    :param body:
    :return:
    """
    try:
        game = GameReceiver(get_dolphin(), json.loads(body))
        game.save()
    except Exception as e:
        logging.error("Failed to save game: %s", e)
    # Send ACK.
    channel.basic_ack(delivery_tag=method.delivery_tag)


def game_result_receiver():
    """
    This task register callback function on getting user results.
    :return:
    """
    rabbit = get_rabbit()
    init_rabbit(rabbit)
    rabbit_channel = rabbit.channel()
    rabbit_channel.basic_qos(prefetch_count=1)
    rabbit_channel.basic_consume(
        game_result_receiver_callback,
        queue="game.result"
    )
    rabbit_channel.start_consuming()


def user_result_receiver_callback(channel, method, properties, body):
    """
    This function gets user results and handle it with UserReceiver class.
    :param channel:
    :param method:
    :param properties:
    :param body:
    :return:
    """
    try:
        user = UserReceiver(get_dolphin(), json.loads(body))
        user.save()
    except Exception as e:
        logging.error("Failed to save user: %s", e)
    # Send ACK.
    channel.basic_ack(delivery_tag=method.delivery_tag)


def user_result_receiver():
    """
    This task register callback function on getting user results.
    :return:
    """
    rabbit = get_rabbit()
    init_rabbit(rabbit)
    rabbit_channel = rabbit.channel()
    rabbit_channel.basic_qos(prefetch_count=1)
    rabbit_channel.basic_consume(
        user_result_receiver_callback,
        queue="user.result"
    )
    rabbit_channel.start_consuming()


def user_spider_checker_callback(channel, method, properties, body):
    """
    This function checks if a user should be crawled.
    :param channel:
    :param method:
    :param properties:
    :param body:
    :return:
    """
    try:
        user_order = UserOrderReceiver(
            get_dolphin(),
            user_spider_checker_pub_channel,
            json.loads(body),
            args.user_expire_interval
        )
        user_order.issue()
    except Exception as e:
        logging.error("Failed to save review: %s", e)
    # Send ACK.
    channel.basic_ack(delivery_tag=method.delivery_tag)


def user_spider_checker():
    """
    This function checks if a user should be crawled.
    :return:
    """
    global user_spider_checker_pub_channel
    rabbit = get_rabbit()
    init_rabbit(rabbit)
    user_spider_checker_pub_channel = rabbit.channel()
    rabbit_channel = rabbit.channel()
    rabbit_channel.basic_qos(prefetch_count=1)
    rabbit_channel.basic_consume(
        user_spider_checker_callback,
        queue="user.order.pre"
    )
    rabbit_channel.start_consuming()


def review_result_receiver_callback(channel, method, properties, body):
    """
    This function gets review results and handle it with ReviewReceiver class.
    :param channel:
    :param method:
    :param properties:
    :param body:
    :return:
    """
    try:
        review = ReviewReceiver(get_dolphin(), json.loads(body))
        review.add_stat()
        review.save()
    except Exception as e:
        logging.error("Failed to save review: %s", e)
    # Send ACK.
    channel.basic_ack(delivery_tag=method.delivery_tag)


def review_result_receiver():
    """
    This task register callback function on getting review results.
    :return:
    """
    rabbit = get_rabbit()
    init_rabbit(rabbit)
    rabbit_channel = rabbit.channel()
    rabbit_channel.basic_qos(prefetch_count=1)
    rabbit_channel.basic_consume(
        review_result_receiver_callback,
        queue="review.result"
    )
    rabbit_channel.start_consuming()


def review_spider_issuer():
    """
    This task issue orders to the review spider to crawl reviews.
    :return:
    """
    while True:
        dolphin = get_dolphin()
        rabbit = get_rabbit()
        init_rabbit(rabbit)
        query_sql = "SELECT `appid`, `crawled_at` FROM `apps` WHERE `crawled_at` < %s AND `is_concerned` = 1"
        update_sql = "UPDATE `apps` SET `crawled_at` = %s WHERE `appid` = %s"
        issue_interval = args.review_interval
        this_time = int(time.time())
        time_since = this_time - issue_interval
        review_language = args.review_language
        try:
            with dolphin.cursor() as cursor:
                # Query apps haven't be crawled in some time.
                cursor.execute(query_sql, (time_since,))
                results = cursor.fetchall()
            with rabbit.channel() as channel:
                # Publish review crawl orders.
                for app in results:
                    app["language"] = review_language
                    app["last_crawled"] = app["crawled_at"]
                    channel.basic_publish(
                        exchange="ubi",
                        routing_key="review.order",
                        body=json.dumps(app),
                        properties=pika.BasicProperties(delivery_mode=2, )
                    )
                    logging.info(
                        "Issued a review order of app [%d] since [%d] in [%s]",
                        app["appid"],
                        app["last_crawled"],
                        app["language"]
                    )
                    with dolphin.cursor() as cursor:
                        # Update "last_crawled".
                        cursor.execute(update_sql, (this_time, app["appid"]))
            dolphin.commit()
        except Exception as e:
            logging.error("An error occurred while issuing review orders: %s", e)
        finally:
            dolphin.close()
        # Let's sleep.
        time.sleep(issue_interval // 2)


def main():
    global args
    # Initialise logging.
    init_logging("controller")
    # Parse arguments.
    args = parse_arguments()
    # Start tasks.
    """ This task issues orders to crawl reviews. """
    review_spider_issuer_thread = threading.Thread(
        target=review_spider_issuer,
        name="ReviewSpiderIssuer"
    )
    review_spider_issuer_thread.setDaemon(True)
    review_spider_issuer_thread.start()
    """ This task saves reviews and count changes. """
    review_result_receiver_thread = threading.Thread(
        target=review_result_receiver,
        name="ReviewResultReceiver"
    )
    review_result_receiver_thread.setDaemon(True)
    review_result_receiver_thread.start()
    """ This task checks orders to crawl users. """
    user_spider_checker_thread = threading.Thread(
        target=user_spider_checker,
        name="UserSpiderChecker"
    )
    user_spider_checker_thread.setDaemon(True)
    user_spider_checker_thread.start()
    """ This task saves user data. """
    user_result_receiver_thread = threading.Thread(
        target=user_result_receiver,
        name="UserResultReceiver"
    )
    user_result_receiver_thread.setDaemon(True)
    user_result_receiver_thread.start()
    """ This task checks orders to crawl games. """
    game_spider_checker_thread = threading.Thread(
        target=game_spider_checker,
        name="GameSpiderChecker"
    )
    game_spider_checker_thread.setDaemon(True)
    game_spider_checker_thread.start()
    """ This task saves game data. """
    game_result_receiver_thread = threading.Thread(
        target=game_result_receiver,
        name="GameResultReceiver"
    )
    game_result_receiver_thread.setDaemon(True)
    game_result_receiver_thread.start()
    """ This task saves weights. """

    while True:
        time.sleep(3600)


def get_dolphin():
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
        cursorclass=pymysql.cursors.DictCursor
    )
    return dolphin


def get_rabbit():
    """
    Get an instance of pika for RabbitMQ.
    :return:
    """
    rabbit_params = pika.URLParameters(args.mq_url)
    rabbit_params.heartbeat = 0
    rabbit = pika.BlockingConnection(rabbit_params)
    return rabbit


def parse_arguments():
    """
    Parse arguments from command line and return the results.
    :return: parsed args
    """
    parser = argparse.ArgumentParser(description="PB Central Controller.")
    parser.add_argument("--debug", action="store_true",
                        help="Use this option to enable debug mode.")
    parser.add_argument("--rabbit-mq-url", action="store", dest="mq_url",
                        default="amqp://guest:guest@localhost:5672/%2F",
                        help="Specify RabbitMQ connection URL.")
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
    parser.add_argument("--review-spider-language", action="store",
                        dest="review_language", default="all",
                        help="Specify reviews of what language to crawl.")
    parser.add_argument("--review-spider-interval", action="store",
                        dest="review_interval", default=3600 * 24, type=int,
                        help="Specify interval between review crawls in seconds.")
    parser.add_argument("--user-expire-interval", action="store",
                        dest="user_expire_interval", default=3600 * 24 * 7, type=int,
                        help="Specify interval before a user's data expires.")
    return parser.parse_args()


if __name__ == "__main__":
    main()
