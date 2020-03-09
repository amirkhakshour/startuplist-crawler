import json

import pika
from pika.exceptions import ChannelWrongStateError
from scrapy.utils.serialize import ScrapyJSONEncoder


class RabbitMQItemPublisherPipeline(object):
    def __init__(self, host, port, user, password, virtual_host, exchange_name, routing_key, queue_name):
        self.connection = None
        self.channel = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.virtual_host = virtual_host
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.queue_name = queue_name
        credentials = pika.PlainCredentials(self.user, self.password)
        self.parameters = pika.ConnectionParameters(self.host,
                                                    self.port,
                                                    self.virtual_host,
                                                    credentials)

        self.encoder = ScrapyJSONEncoder()
        self.connect()

    def connect(self):
        self.connection = pika.BlockingConnection(parameters=self.parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name,
                                      exchange_type="direct",
                                      durable=True)
        self.channel.queue_declare(queue=self.queue_name,
                                   durable=True)
        self.channel.queue_bind(exchange=self.exchange_name,
                                routing_key=self.routing_key,
                                queue=self.queue_name)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get("RABBITMQ_HOST"),
            port=crawler.settings.get("RABBITMQ_PORT"),
            user=crawler.settings.get("RABBITMQ_USER"),
            password=crawler.settings.get("RABBITMQ_PASSWORD"),
            virtual_host=crawler.settings.get("RABBITMQ_VIRTUAL_HOST"),
            exchange_name=crawler.settings.get("RABBITMQ_EXCHANGE"),
            routing_key=crawler.settings.get("RABBITMQ_ROUTING_KEY"),
            queue_name=crawler.settings.get("RABBITMQ_QUEUE"),
        )

    def close_spider(self, spider):
        self.channel.close()
        self.connection.close()

    def process_item(self, item, spider):
        data = self.encoder.encode(item)
        try:
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key,
                body=data,
                properties=pika.BasicProperties(
                    headers={'model': item.get('model', None)}
                ),
            )
        except ChannelWrongStateError as e:
            self.connect()
        return item
