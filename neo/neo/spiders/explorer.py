# -*- coding: utf-8 -*-
import scrapy


class ExplorerSpider(scrapy.Spider):
    name = 'explorer'
    amqp_queue_name = 'scrapy_fetcher'
    amqp_routing_key = 'fetch.logo'

    def _make_request(self, mframe, hframe, body):
        url = body.decode()
        return scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        print("response", response.url)
