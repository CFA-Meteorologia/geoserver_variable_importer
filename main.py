#!/usr/bin/env python
import json
import os
import shutil
import sys

import pika

import initializations
from config import get_config
from helpers import update_geoserver_layer

temp_dir = get_config('temp_dir')


def callback(ch, method, properties, body):
    try:
        shutil.rmtree(temp_dir)
    except FileNotFoundError:
        pass
    os.mkdir(temp_dir)

    data = json.loads(body.decode())
    print(F" [ ] Received var: {data['var']}, domain: {data['domain']} from {data['date']}")

    update_geoserver_layer(
        data['var'],
        data['data'],
        data['bounds'],
        data['date'].replace('T', '_'),
        data['projection'],
        data['domain'],
    )

    print(F" [x] Processed var: {data['var']}, domain: {data['domain']} from {data['date']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


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
