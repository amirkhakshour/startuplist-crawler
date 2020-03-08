# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NeoItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    source_url = scrapy.Field()
    website = scrapy.Field()
    pitch = scrapy.Field()
    description = scrapy.Field()
    images = scrapy.Field()
