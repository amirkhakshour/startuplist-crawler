import pika
import logging
import time

from pika.exceptions import ChannelWrongStateError

logger = logging.getLogger(__name__)

DEFAULT_RABBITMQ_EXCHANGE_TYPE = 'direct'
DEFAULT_RABBITMQ_QUEUE = 'scrapy'
DEFAULT_RABBITMQ_ROUTING_KEY = 'scrapy.items'


class RabbitMQConnection(object):
    def __init__(self, connection_url, exchange_name,
                 exchange_type=DEFAULT_RABBITMQ_EXCHANGE_TYPE,
                 routing_key=DEFAULT_RABBITMQ_ROUTING_KEY,
                 queue_name=DEFAULT_RABBITMQ_QUEUE,
                 bind=True):
        self.connection = None
        self.channel = None
        self.connection_url = connection_url
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.routing_key = routing_key
        self.queue_name = queue_name
        self.bind = bind  # where create and bind the queue or not
        self.connect()

    def connect(self):
        if self.connection:
            try:
                self.close()
            except:
                pass
        self.connection = pika.BlockingConnection(pika.URLParameters(self.connection_url))
        self.channel = self.connection.channel()
        if self.bind:
            self.bind_channel()

    def bind_channel(self):
        """Declare and create exchange and bind the queue with it"""
        self.channel.exchange_declare(exchange=self.exchange_name,
                                      exchange_type=self.exchange_type,
                                      durable=True)
        self.channel.queue_declare(queue=self.queue_name,
                                   durable=True)
        self.channel.confirm_delivery()
        self.channel.queue_bind(exchange=self.exchange_name,
                                routing_key=self.routing_key,
                                queue=self.queue_name)

    def close(self):
        print("Closing RabbitMQ connection.")
        self.channel.close()
        self.connection.close()

    def _try_operation(func):
        """Wrap unary method by reconnect procedure"""

        def wrapper(self, *args, **kwargs):
            retries = 0
            while retries < 10:
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    retries += 1
                    msg = 'func %s failed. Reconnecting... (%d times). \n message: %s' % \
                          (str(func), retries, str(e))
                    logger.info(msg)
                    self.connect()
                    time.sleep((retries - 1) * 5)
            return None

        return wrapper

    @_try_operation
    def retrieve(self, auto_ack=False):
        """Pop a message"""
        return self.channel.basic_get(queue=self.queue_name, auto_ack=auto_ack)

    @_try_operation
    def publish(self, body, headers=None):
        """
        publish a message to bounded queue
        Available options to pass from kwargs to basic_publish:
        1- body :a jsonable object
        2- headers: pika header properties
        :return:
        """
        properties = None
        if headers:
            properties = pika.BasicProperties(headers=headers)
        try:
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key,
                body=body,
                properties=properties
            )
        except ChannelWrongStateError as e:
            self.connect()

    def __len__(self):
        """Return the length of the queue"""
        declared = self.channel.queue_declare(self.queue_name, passive=True)
        return declared.method.message_count

    @_try_operation
    def ack(self, delivery_tag):
        """Ack a message"""
        self.channel.basic_ack(delivery_tag=delivery_tag)

    def clear(self):
        """Clear queue/stack"""
        self.channel.queue_purge(self.key)
