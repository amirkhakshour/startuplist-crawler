# -*- coding: utf-8 -*-
import scrapy
from neo.items import StartupItemUpdate
from . import ExplorerSpiderMixin


class ExplorerSpider(ExplorerSpiderMixin, scrapy.Spider):
    name = 'explorer_meta'
    # fetcher details
    amqp_fetcher_queue_name = 'scrapy_fetch_meta'
    amqp_fetcher_routing_key = 'meta'

    # amqp result details
    amqp_result_routing_key = 'startup.email'

    LOGO_FINDER_PRIORITY = [
        '//meta[@property="og:image"]/@content',
        '//meta[@name="twitter:card"]/@content',
    ]

    def _make_request(self, mframe, hframe, body):
        url = body.decode()
        return scrapy.Request(url, callback=self.parse, meta={'website': url})

    def parse(self, response):
        startup_logo = None
        for path in self.LOGO_FINDER_PRIORITY:
            startup_logo = response.xpath(path).get()
            if startup_logo:
                break

        if not startup_logo:
            startup_logo = response.xpath('//header/descendant::img/@src').get()

        startup_logo = response.urljoin(startup_logo) if startup_logo else ''
        startup_title = self.clean_text(response.xpath('//meta[@property="og:title"]/@content').get())
        startup_description = self.clean_text(response.xpath('//meta[@property="og:description"]/@content').get())

        yield StartupItemUpdate({
            'model': 'StartupItemUpdate',
            'website': response.meta['website'],
            'data': {
                'startup_logo': startup_logo,
                'startup_title': startup_title,
                'startup_description': startup_description,
            }
        })
