# -*- coding: utf-8 -*-
import re
import scrapy
from neo.items import StartupItem, StartupDataItem, StartupImage
from neo.utils import email_regex, INNER_PAGES_ULR


class StartupListSpider(scrapy.Spider):
    name = 'startuplist'
    start_urls = ['https://startups-list.com/']

    def get_emails_from_response(self, response):
        text = response.body.decode('utf-8')
        """Returns an iterator of matched emails found in string s."""
        # Removing lines that start with '//' because the regular expression
        # mistakenly matches patterns like 'http://foo@bar.com' as '//foo@bar.com'.
        return set([email[0] for email in re.findall(email_regex, text)
                    if not (email[0].startswith('//') or '/' in email[0])])

    def parse(self, response):
        for city in response.xpath("//a[contains(@class, 'citylink')]"):
            city_url = response.urljoin(city.xpath('./@href').get())
            city_text = city.xpath('./h3/text()').get().strip().lower()
            yield scrapy.Request(
                url=city_url,
                callback=self.extract_city_page,
                meta={'city': city_text}
            )
        # Beta locations
        for city in response.xpath("//h2[contains(text(),'%s')]/following::a[contains(@class, 'label')]" % 'Beta Locations'):
            city_url = response.urljoin(city.xpath('./@href').get())
            city_text = city.xpath('./text()').get().strip().lower()
            yield scrapy.Request(
                url=city_url,
                callback=self.extract_city_page,
                meta={'city': city_text}
            )

    def extract_city_page(self, response):
        startup_cards = response.xpath('//div[contains(concat(" ", @class, " "), " card startup ")]')
        if not startup_cards:  # check if no card, break pager
            return
        for startup_link in startup_cards:
            main_link = startup_link.xpath('./a[@class="main_link"]')
            website = main_link.xpath('./@href').get()
            startup_name = main_link.xpath(
                './descendant::h1/text()'
            ).get().replace('/n', '')
            startup_description = startup_link.xpath('./descendant::p').get()
            startup_pitch = startup_link.xpath('./descendant::p/strong/text()').get()
            startup_logo = startup_link.xpath('./descendant::img[@property="image"]/@data-src').get()
            tags = startup_link.xpath('./descendant::img/@alt').get().split()
            tags = [item.lower().strip() for item in tags]
            # add tags
            data = [{
                'data_type': self.settings.get('STARTUP_DATA_TYPE_TAGS'),
                'data': tags,
            }]
            city = response.meta['city']
            data.append({
                'data_type': self.settings.get('STARTUP_DATA_TYPE_CITY'),
                'data': city,
            })

            # the visit page is redirected to the main startup page
            item_data = {
                'name': startup_name,
                'website': website,
                'source_url': response.urljoin(response.url),
                'pitch': startup_pitch or '',
                'description': startup_description,
                'data': data,
            }
            print('#' * 100)
            print(item_data)
            # yield scrapy.Request(
            #     url=response.urljoin(website),
            #     callback=self.extract_startup_url,
            #     meta={'item_data': item_data, 'logo': startup_logo}
            # )

    def extract_startup_url(self, response):
        item_data = response.meta['item_data']
        item_data.update({
            'model': 'Startup',
        })
        emails_found = self.get_emails_from_response(response)
        if emails_found:
            item_data['data'].append({
                'data_type': self.settings.get('STARTUP_DATA_TYPE_EMAIL'),
                'data': {
                    'emails': emails_found,
                }
            })
        # send in any case
        yield StartupItem(**item_data)
        yield StartupImage(**{
            'model': 'StartupImage',
            'website': item_data['website'],
            'images': [response.meta['logo'], ]
        })

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
                'model': 'StartupData',
                'data_type': self.settings.get('STARTUP_DATA_TYPE_EMAIL'),
                'data': {
                    'emails': emails_found,
                }
            }
            yield StartupDataItem(**item_data)
