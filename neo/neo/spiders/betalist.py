# -*- coding: utf-8 -*-
import scrapy


class BetalistSpider(scrapy.Spider):
    name = 'betalist'
    start_urls = ['https://betalist.com/regions/']

    def parse(self, response):
        for region in response.xpath("//a[contains(@class, 'tag--card')]"):
            region_url = response.urljoin(region.xpath('./@href').extract().pop())
            region_text = region.xpath('./text()').extract().pop().strip().lower()
            yield scrapy.Request(
                url=region_url,
                callback=self.extract_region_page,
                meta={'region': region_text}
            )

    def extract_region_page(self, response):
        pass
