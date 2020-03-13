import time
import signal
import logging

from neo.rabbitmqlink.connection import RabbitMQConnection

logger = logging.getLogger(__name__)


class IScheduler(object):
    """ Base Scrapy scheduler class. """

    def __init__(self):
        raise NotImplementedError

    def open(self, spider):
        """Start scheduling"""
        raise NotImplementedError

    def close(self, reason):
        """Stop scheduling"""
        raise NotImplementedError

    def enqueue_request(self, request):
        """Add request to queue"""
        raise NotImplementedError

    def next_request(self):
        """Pop a request"""
        raise NotImplementedError

    def has_pending_requests(self):
        """Check if queue is not empty"""
        raise NotImplementedError


class Scheduler(IScheduler):
    # TODO: to be extended in future
    @staticmethod
    def _ensure_settings(settings, key):
        if not settings.get(key):
            msg = 'Please set "{}" at settings.'.format(key)
            raise ValueError(msg)


class RabbitMQScheduler(Scheduler):
    """ A RabbitMQ Scheduler for Scrapy. """
    queue = None
    stats = None

    def __init__(self, connection_url, exchange_name, *args, **kwargs):
        self.connection_url = connection_url
        self.exchange_name = exchange_name
        self.waiting = False
        self.closing = False

    @classmethod
    def from_settings(cls, settings):
        cls._ensure_settings(settings, 'RABBITMQ_FETCHER_URI')
        cls._ensure_settings(settings, 'RABBITMQ_FETCH_EXCHANGE')
        connection_url = settings.get('RABBITMQ_FETCHER_URI')
        exchange_name = settings.get('RABBITMQ_FETCH_EXCHANGE')
        return cls(connection_url, exchange_name)

    @classmethod
    def from_crawler(cls, crawler):
        scheduler = cls.from_settings(crawler.settings)
        scheduler.stats = crawler.stats
        signal.signal(signal.SIGINT, scheduler.on_sigint)
        return scheduler

    def __len__(self):
        return len(self.queue)

    def open(self, spider):
        if not hasattr(spider, '_make_request'):
            msg = 'Method _make_request not found in spider. '
            msg += 'Please add it to spider or see manual at '
            raise NotImplementedError(msg)

        if not hasattr(spider, 'amqp_fetcher_queue_name'):
            msg = 'Please set amqp_fetcher_queue_name parameter to spider. '
            raise ValueError(msg)

        if not hasattr(spider, 'amqp_fetcher_routing_key'):
            msg = 'Please set amqp_fetcher_routing_key parameter to spider. '
            raise ValueError(msg)

        self.spider = spider
        self.queue = self.get_connection_queue(spider.amqp_fetcher_queue_name, spider.amqp_fetcher_routing_key)

        msg_count = len(self.queue)
        if msg_count:
            logger.info('Resuming crawling ({} urls scheduled)'
                        .format(msg_count))
        else:
            logger.info('No items to crawl in {}'
                        .format(self.queue.queue_name))

    def get_connection_queue(self, queue_name, routing_key):
        return RabbitMQConnection(self.connection_url,
                                  exchange_name=self.exchange_name,
                                  queue_name=queue_name,
                                  routing_key=routing_key)

    def on_sigint(self, signal, frame):
        self.closing = True

    def close(self, reason):
        self.queue.close()

    def enqueue_request(self, request):
        """ Enqueues request to main queues back
        """
        if self.queue:
            if self.stats:
                self.stats.inc_value('scheduler/enqueued/rabbitmq',
                                     spider=self.spider)
            self.queue.publish(request.url)
        return True

    def next_request(self):
        """ Creates and returns a request to fire
        """
        if self.closing:
            return

        mframe, hframe, body = self.queue.retrieve()
        if any([mframe, hframe, body]):
            self.waiting = False

            if self.stats:
                self.stats.inc_value('scheduler/dequeued/rabbitmq',
                                     spider=self.spider)

            request = self.spider._make_request(mframe, hframe, body)
            request.meta['delivery_tag'] = mframe.delivery_tag
            logger.info('Running request {}'.format(request.url))
            return request
        else:
            if not self.waiting:
                msg = 'Queue {} is empty. Waiting for messages...'
                self.waiting = True
                logger.info(msg.format(self.queue.queue_name))
            time.sleep(1)
            return None

    def has_pending_requests(self):
        return not self.closing

    def ack_message(self, delivery_tag):
        self.queue.ack(delivery_tag)

    def requeue_message(self, body, headers=None):
        self.queue.publish(body, headers)
