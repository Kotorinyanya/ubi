#!/usr/bin/env python3
import argparse
import json
import logging
import pika
from libs.helper import init_logging
from libs.helper import init_rabbit
from libs.spiders import UserSpider

rabbit = None


def parse_arguments():
    """
    Parse arguments from command line and return the results.
    :return: parsed args
    """
    parser = argparse.ArgumentParser(description="PB User Spider.")
    parser.add_argument("--debug", action="store_true",
                        help="Use this option to enable debug mode.")
    parser.add_argument("--rabbit-mq-url", action="store", dest="mq_url",
                        default="amqp://guest:guest@localhost:5672/%2F",
                        help="Specify RabbitMQ connection URL.")
    return parser.parse_args()


def order_callback(channel, method, properties, body):
    """
    Handle orders.
    Call real spider to crawl reviews and send ACK after finishing.
    :param channel:
    :param method:
    :param properties:
    :param body:
    :return:
    """
    global rabbit
    try:
        order = json.loads(body.decode())
        logging.info(
            "Start crawling user [%s]",
            str(order["steamid"])
        )
        spider = UserSpider(
            order["steamid"],
            channel,
            method,
            rabbit.channel()
        )
        spider.crawl()
    except (AttributeError, json.decoder.JSONDecodeError, TypeError, KeyError):
        logging.error("Failed to parse order: %s", body)
    # Send ACK.
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    global rabbit
    # Initialise logging.
    init_logging("user")
    # Parse arguments.
    args = parse_arguments()
    # Establish MQ connection.
    rabbit_params = pika.URLParameters(args.mq_url)
    rabbit_params.heartbeat = 0
    rabbit = pika.BlockingConnection(rabbit_params)
    # Declare exchange & queues.
    init_rabbit(rabbit)
    # Set up subscription and start consuming.
    rabbit_channel = rabbit.channel()
    rabbit_channel.basic_qos(prefetch_count=1)
    rabbit_channel.basic_consume(order_callback, queue="user.order")
    rabbit_channel.start_consuming()


if __name__ == "__main__":
    main()
