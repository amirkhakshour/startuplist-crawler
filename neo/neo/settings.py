# -*- coding: utf-8 -*-
import os

# Scrapy settings for neo project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'neo'

SPIDER_MODULES = ['neo.spiders']
NEWSPIDER_MODULE = 'neo.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 0.5
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'neo.middlewares.NeoSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#     'scrapy_crawlera.CrawleraMiddleware': 610,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'neo.pipelines.NeoPipeline': 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

ITEM_PIPELINES = {
    'neo.pipelines.RabbitMQItemPublisherPipeline': 300,
}

RABBITMQ_RESULT_HOST = os.environ.get('RABBITMQ_RESULT_HOST', 'localhost')
RABBITMQ_RESULT_PORT = os.environ.get('RABBITMQ_RESULT_PORT', 55672)
RABBITMQ_RESULT_USER = os.environ.get('RABBITMQ_RESULT_USER', 'admin')
RABBITMQ_RESULT_PASSWORD = os.environ.get('RABBITMQ_RESULT_PASSWORD', 'doogh')
RABBITMQ_RESULT_VHOST = os.environ.get('RABBITMQ_RESULT_VHOST', '3meg')
RABBITMQ_RESULT_EXCHANGE = os.environ.get('RABBITMQ_RESULT_EXCHANGE', 'scrapy')
RABBITMQ_RESULT_QUEUE = os.environ.get('RABBITMQ_RESULT_QUEUE', 'startups')
RABBITMQ_RESULT_ROUTING_KEY = os.environ.get('RABBITMQ_RESULT_ROUTING_KEY', 'startups')
RABBITMQ_RESULT_URI = 'amqp://{user}:{passwd}@{host}:{port}/{vhost}'.format(
    user=RABBITMQ_RESULT_USER,
    passwd=RABBITMQ_RESULT_PASSWORD,
    host=RABBITMQ_RESULT_HOST,
    port=RABBITMQ_RESULT_PORT,
    vhost=RABBITMQ_RESULT_VHOST
)

RABBITMQ_FETCH_HOST = os.environ.get('RABBITMQ_FETCH_HOST', 'localhost')
RABBITMQ_FETCH_PORT = os.environ.get('RABBITMQ_FETCH_PORT', 55672)
RABBITMQ_FETCH_USER = os.environ.get('RABBITMQ_FETCH_USER', 'admin')
RABBITMQ_FETCH_PASSWORD = os.environ.get('RABBITMQ_FETCH_PASSWORD', 'doogh')
RABBITMQ_FETCH_VIRTUAL_HOST = os.environ.get('RABBITMQ_FETCH_VIRTUAL_HOST', '3meg')
RABBITMQ_FETCH_EXCHANGE = os.environ.get('RABBITMQ_FETCH_EXCHANGE', 'scrapy')
RABBITMQ_FETCH_QUEUE = os.environ.get('RABBITMQ_FETCH_QUEUE', 'fetcher')
RABBITMQ_FETCH_ROUTING_KEY = os.environ.get('RABBITMQ_FETCH_ROUTING_KEY', 'startups')
RABBITMQ_FETCHER_URI = 'amqp://{user}:{passwd}@{host}:{port}/{vhost}'.format(
    user=RABBITMQ_FETCH_USER,
    passwd=RABBITMQ_FETCH_PASSWORD,
    host=RABBITMQ_FETCH_HOST,
    port=RABBITMQ_FETCH_PORT,
    vhost=RABBITMQ_FETCH_VIRTUAL_HOST
)
STARTUP_DATA_TYPE_EMAIL = 'E'
STARTUP_DATA_TYPE_PEOPLE = 'P'
STARTUP_DATA_TYPE_PHONE = 'H'
STARTUP_DATA_TYPE_MISC = 'M'
STARTUP_DATA_TYPE_TAGS = 'T'
STARTUP_DATA_TYPE_REGION = 'R'
STARTUP_DATA_TYPE_CITY = 'C'

CRAWLERA_ENABLED = True
CRAWLERA_APIKEY = '4d9b378bdf78449bbef0393efcc5bb20'


# Enable RabbitMQ scheduler
SCHEDULER = "neo.rabbitmqlink.scheduler.RabbitMQScheduler"
# Middleware acks RabbitMQ message on success
DOWNLOADER_MIDDLEWARES = {
    'neo.rabbitmqlink.middleware.RabbitMQMiddleware': 999
}
