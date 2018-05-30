import logging
import sys
import time

MQ_EXCHANGE = "ubi"
MQ_QUEUES = [
    "review.order",
    "review.result",
    "user.order.pre",
    "user.order",
    "user.result",
    "game.order.pre",
    "game.order",
    "game.result"
]


def init_logging(prefix, level="INFO"):
    # Init rules
    logger = logging.getLogger()
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    log_file = sys.path[0] + "/logs/" + prefix + "-" + timestamp + ".log"
    formatter = "[%(asctime)s] [%(threadName)s] [%(levelname)s] %(message)s"
    fh = logging.FileHandler(log_file, encoding="utf-8")
    # Apply the rules and add stdout logger
    logging.basicConfig(level=level, format=formatter)
    fh.setFormatter(logging.Formatter(formatter))
    logger.addHandler(fh)


def init_rabbit(rabbit):
    channel = rabbit.channel()
    # Declare the exchange.
    channel.exchange_declare(
        exchange=MQ_EXCHANGE,
        exchange_type="topic",
        durable=True
    )
    # Declare the queues.
    for queue in MQ_QUEUES:
        channel.queue_declare(queue=queue, durable=True)
        channel.queue_bind(
            exchange=MQ_EXCHANGE,
            queue=queue,
            routing_key=queue
        )
