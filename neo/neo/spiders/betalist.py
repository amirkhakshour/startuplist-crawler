# -*- coding: utf-8 -*-
import re
import scrapy
from neo.items import StartupItem, StartupDataItem

email_regex = re.compile((r"([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                          "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                          "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))
INNER_PAGES_ULR = {
    'contact',
    'contact-us',
    'contactus',
    'about',
    'about-us',
    'impressum',
    'imprint',
    'privacy',
}


class BetalistSpider(scrapy.Spider):
    name = 'betalist'
    start_urls = ['https://betalist.com/regions/']

    def __init__(self, **kwargs):
        super(BetalistSpider, self).__init__(**kwargs)

    def get_emails_from_response(self, response):
        text = response.body.decode('utf-8')
        """Returns an iterator of matched emails found in string s."""
        # Removing lines that start with '//' because the regular expression
        # mistakenly matches patterns like 'http://foo@bar.com' as '//foo@bar.com'.
        return set([email[0] for email in re.findall(email_regex, text)
                    if not (email[0].startswith('//') or '/' in email[0])])

    def parse(self, response):
        for region in response.xpath("//a[contains(@class, 'tag--card')]"):
            region_url = response.urljoin(region.xpath('./@href').get())
            region_text = region.xpath('./text()').get().strip().lower()
            if region_text != 'germany':
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
            yield scrapy.Request(
                url=response.urljoin(startup_link.get()),
                callback=self.extract_startup_page,
                meta=response.meta
            )

    def extract_startup_page(self, response):
        startup_name = response.xpath(
            "//h1[contains(@class, 'startup__summary__name')]/text()"
        ).get()
        startup_pitch = response.xpath('//h2[@class="startup__summary__pitch"]/text()').get()
        startup_description = response.xpath('//div[@class="startup__description"]').get()
        startup_srcs = response.xpath('//a[@class="carousel__item"]/img/@src').extract()
        startup_visit_url = response.xpath("//a[contains(text(),'%s')]/@href" % 'Visit Site').get()

        # add tags
        tags = response.xpath('//div[@class="markets"]/descendant::a[@class="tag"]/text()').extract()
        data = [{
            'data_type': self.settings.get('STARTUP_DATA_TYPE_TAGS'),
            'data': tags,
        }]

        # add region data from metadata
        region = response.meta['region']
        data.append({
            'data_type': self.settings.get('STARTUP_DATA_TYPE_REGION'),
            'data': region,
        })

        for maker in response.xpath('//div[@class="maker"]'):
            maker_role = maker.xpath('./descendant::a[@class="maker__role"]/text()').get()
            maker_base = maker.xpath('./descendant::a[@class="maker__name"]')
            maker_twitter_url = maker_base.xpath('./@href').get()
            maker_name = maker_base.xpath('./text()').get()
            data.append({
                'data_type': self.settings.get('STARTUP_DATA_TYPE_PEOPLE'),
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
        item_data = response.meta['item_data']
        item_data.update({
            'model': 'Startup',
            'website': response.url,
        })
        emails_found = self.get_emails_from_response(response)
        if emails_found:
            item_data['data'].append({
                'data_type': self.settings.get('STARTUP_DATA_TYPE_EMAIL'),
                'data': {
                    'emails': emails_found,
                }
            })
        yield StartupItem(**item_data)
        if not emails_found:
            # if we found no emails start parsing other pages
            item_data = {  # Remove unnecessary data
                'website': item_data['website'],
            }
            for page in INNER_PAGES_ULR:
                yield scrapy.Request(
                    url=response.urljoin(page),
                    callback=self.extract_data_from_page,
                    meta={'item_data': item_data}
                )

    def extract_data_from_page(self, response):
        item_data = response.meta['item_data']
        emails_found = self.get_emails_from_response(response)
        if emails_found:
            item_data['data'] = {
                'model': 'StartupDataItem',
                'data_type': self.settings.get('STARTUP_DATA_TYPE_EMAIL'),
                'data': {
                    'emails': emails_found,
                }
            }
            yield StartupDataItem(**item_data)
