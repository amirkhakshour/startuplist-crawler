from scrapy.utils.serialize import ScrapyJSONEncoder
from neo.rabbitmqlink.connection import RabbitMQConnection


class RabbitMQItemPublisherPipeline(object):
    def __init__(self, connect_url, exchange_name, routing_key, queue_name):
        self.connect_url = connect_url
        self.connection = RabbitMQConnection(connect_url, exchange_name=exchange_name,
                                             routing_key=routing_key, queue_name=queue_name)
        self.encoder = ScrapyJSONEncoder()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            connect_url=crawler.settings.get("RABBITMQ_RESULT_URL"),
            exchange_name=crawler.settings.get("RABBITMQ_RESULT_EXCHANGE"),
            routing_key=crawler.settings.get("RABBITMQ_RESULT_ROUTING_KEY"),
            queue_name=crawler.settings.get("RABBITMQ_RESULT_QUEUE"),
        )

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        data = self.encoder.encode(item)
        self.connection.publish(body=data, headers={'model': item.get('model', None)})
        return item
