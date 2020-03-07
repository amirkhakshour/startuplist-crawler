# -*- coding: utf-8 -*-
import scrapy


class BetalistSpider(scrapy.Spider):
    name = 'betalist'
    start_urls = ['https://betalist.com/regions/']

    def parse(self, response):
        pass
