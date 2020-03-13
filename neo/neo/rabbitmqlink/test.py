#!/usr/bin/env python
import pika
RABBITMQ_CONNECTION_PARAMETERS = 'amqp://admin:doogh@localhost:55672/3meg'
connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_CONNECTION_PARAMETERS))
channel = connection.channel()

# set queue name
queue_key = 'fetcher.meta'

# publish links to queue
with open('urls.txt') as f:
    for url in f:
        url = url.strip(' \n\r')
        channel.basic_publish(exchange='scrapy',
                              routing_key=queue_key,
                              body=url,
                              properties=pika.BasicProperties(
                                  content_type='text/plain',
                                  delivery_mode=2
                              ))

connection.close()
