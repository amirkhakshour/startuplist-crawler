# -*- coding: utf-8 -*-
import scrapy
from neo.items import StartupItemUpdate
from neo.utils import INNER_PAGES_ULR

from . import ExplorerSpiderMixin


class ExplorerSpider(ExplorerSpiderMixin, scrapy.Spider):
    name = 'explorer_email'
    # fetcher details
    amqp_fetcher_queue_name = 'scrapy_fetch_email'
    amqp_fetcher_routing_key = 'email'

    # amqp result details
    amqp_result_routing_key = 'startup.email'

    def _make_request(self, mframe, hframe, body):
        url = body.decode()
        return scrapy.Request(url, callback=self.parse, meta={'website': url})

    def parse(self, response):
        emails_found = self.get_emails_from_response(response)
        item_data = {
            'website': response.meta['website'],
            'model': 'StartupItemUpdate',
        }
        if emails_found:
            item_data['data'] = {
                'data': {
                    'emails': emails_found,
                }
            }
            yield StartupItemUpdate(**item_data)
        else:
            # if we found no emails start parsing other pages
            item_data = {  # Remove unnecessary data
                'website': item_data['website'],
            }
            for page in INNER_PAGES_ULR:
                yield scrapy.Request(
                    url=response.urljoin(page),
                    callback=self.extract_data_from_page,
                    meta={'item_data': item_data, 'dont_proxy': True}
                )

    def extract_data_from_page(self, response):
        item_data = response.meta['item_data']
        emails_found = self.get_emails_from_response(response)
        if emails_found:
            item_data['data'] = {
                'data': {
                    'emails': emails_found,
                }
            }
            yield StartupItemUpdate(**item_data)
