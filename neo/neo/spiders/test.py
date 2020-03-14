import scrapy


class MySpider(scrapy.Spider):
    name = 'test'
    start_urls = [
        'http://titanmedicalinc.com	',
    ]

    def parse(self, response):
        self.logger.info('A response from %s just arrived!', response.url)
