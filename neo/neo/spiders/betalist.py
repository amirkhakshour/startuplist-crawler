# -*- coding: utf-8 -*-
import scrapy
from neo.items import NeoItem


class BetalistSpider(scrapy.Spider):
    name = 'betalist'
    start_urls = ['https://betalist.com/regions/']

    def __init__(self, **kwargs):
        super(BetalistSpider, self).__init__(**kwargs)
        self.storage = {}

    def parse(self, response):
        for region in response.xpath("//a[contains(@class, 'tag--card')]"):
            region_url = response.urljoin(region.xpath('./@href').get())
            region_text = region.xpath('./text()').get().strip().lower()
            if region_text == 'germany':
                yield scrapy.Request(
                    url=region_url,
                    callback=self.extract_region_page,
                    meta={'region': region_text, 'pager': 1, 'region_url': region_url}
                )

    def extract_region_page(self, response):
        startup_cards = response.xpath("//div[contains(@class, 'startupCard')]")
        if not startup_cards:  # check if no card, break pager
            return

        pager = int(response.meta['pager'])
        region_url = response.meta['region_url']
        next_page = pager + 1
        # crawl next page
        next_page_meta = dict(response.meta)
        next_page_meta['pager'] = next_page
        yield scrapy.Request(
            url=region_url + '/?page=%d' % next_page,
            callback=self.extract_region_page,
            meta=next_page_meta
        )

        for startup_link in response.xpath("//a[contains(@class, 'startupCard__visual')]/@href"):
            response.meta.pop('pager')  # remove pager from meta
            yield scrapy.Request(
                url=response.urljoin(startup_link.get()),
                callback=self.extract_startup_page,
                meta=response.meta
            )
            break

    def extract_startup_page(self, response):
        startup_name = response.xpath(
            "//h1[contains(@class, 'startup__summary__name')]/text()"
        ).get()
        startup_pitch = response.xpath('//h2[@class="startup__summary__pitch"]/text()').get()
        startup_description = response.xpath('//div[@class="startup__description"]').get()
        startup_srcs = response.xpath('//a[@class="carousel__item"]/img/@src').extract()
        startup_visit_url = response.xpath("//a[contains(text(),'%s')]/@href" % 'Visit Site').get()

        data = []
        for maker in response.xpath('/a[@class="maker"]'):
            maker_role = maker.xpath('./descendant::a[@class="maker__role"]/text()').get()
            maker_base = maker.xpath('./descendant::a[@class="maker__name"]')
            maker_twitter_url = maker_base.xpath('./@href').get()
            maker_name = maker_base.xpath('./text()').get()
            data.append({
                'data_type': scrapy.settings.get('STARTUP_DATA_TYPE_PEOPLE'),
                'data': {
                    'name': maker_name,
                    'role': maker_role,
                    'twitter': maker_twitter_url,
                }
            })

        # the visit page is redirected to the main startup page
        item_data = {
            'name': startup_name,
            'source_url': response.urljoin(response.url),
            'pitch': startup_pitch,
            'description': startup_description,
            'images': startup_srcs,
            'data': data,
        }
        yield scrapy.Request(
            url=response.urljoin(startup_visit_url),
            callback=self.extract_startup_url,
            meta={'item_data': item_data}
        )

    def extract_startup_url(self, response):
        itrem_data = response.meta['item_data']
        itrem_data.update({
            'website': response.url
        })
        yield NeoItem(**itrem_data)
