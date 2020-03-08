# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class StartupItem(scrapy.Item):
    model = scrapy.Field()
    name = scrapy.Field()
    source_url = scrapy.Field()
    website = scrapy.Field()
    pitch = scrapy.Field()
    description = scrapy.Field()
    images = scrapy.Field()
    data = scrapy.Field()


class StartupDataItem(scrapy.Item):
    model = scrapy.Field()
    source_url = scrapy.Field()
    type = scrapy.Field()
    data = scrapy.Field()
