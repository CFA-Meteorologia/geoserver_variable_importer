#!/usr/bin/env python
from helpers import update_geoserver_layer
import shutil
import os
from config import get_config
import pika
import sys

temp_dir = get_config('temp_dir')

try:
    shutil.rmtree(temp_dir)
except FileNotFoundError:
    pass
os.mkdir(temp_dir)


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            get_config('rabbitmq.host'),
            port=get_config('rabbitmq.port'),
            credentials=pika.PlainCredentials(
                get_config('rabbitmq.username'),
                get_config('rabbitmq.pass')
            ),
        )
    )
    rabbit_mq_channel = connection.channel()


    rabbit_mq_channel.basic_consume(queue='geoserver-importer', on_message_callback=callback, auto_ack=False)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    rabbit_mq_channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
