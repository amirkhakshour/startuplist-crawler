# -*- coding: utf-8 -*-
import re
import scrapy
from urllib.parse import urlparse, urljoin

from neo.items import StartupItem, StartupDataItem
from neo.utils import email_regex, INNER_PAGES_ULR


class StartupListSpider(scrapy.Spider):
    name = 'startupranking'
    start_urls = ['https://www.startupranking.com/countries']

    def clean_text(self, text):  # todo add Open/Closed principle
        if not text:
            return
        return text\
            .replace('/n', '')\
            .lower()\
            .strip()

    def get_base_url(self, url):
        url = urljoin(url, urlparse(url).path)
        return url.split('?')[0]

    def get_emails_from_response(self, response):
        text = response.body.decode('utf-8')
        """Returns an iterator of matched emails found in string s."""
        # Removing lines that start with '//' because the regular expression
        # mistakenly matches patterns like 'http://foo@bar.com' as '//foo@bar.com'.
        return set([email[0] for email in re.findall(email_regex, text)
                    if not (email[0].startswith('//') or '/' in email[0])])

    def parse(self, response):
        for country in response.xpath("//table[contains(@class, 'table-striped')]/tbody/tr/td[2]/a"):
            country_url = response.urljoin(country.xpath('./@href').get())
            country_text = country.xpath('./text()').get().strip().lower()
            yield scrapy.Request(
                url=country_url,
                callback=self.extract_country_page,
                meta={'country': country_text}
            )

    def extract_country_page(self, response):
        startup_cards = response.xpath('//tbody[@class="ranks"]/tr/td[2]/descendant::a/@href')
        if not startup_cards:  # check if no card, break pager
            return
        for startup_link in startup_cards:
            yield scrapy.Request(
                url=response.urljoin(startup_link.get()),
                callback=self.extract_startup_ref_page,
            )

    def extract_startup_ref_page(self, response):
        info_base_wrapper = response.xpath('//div[@class="su-info"]')
        startup_name = self.clean_text(info_base_wrapper.xpath('./h2/a/text()').get())
        startup_website = self.get_base_url(info_base_wrapper.xpath('./h2/a/@href').get())
        startup_pitch = info_base_wrapper.xpath('./div[@class="su-phrase"]/text()').get()
        startup_description = info_base_wrapper.xpath('./div[@class="su-phrase"]/following::p').get()
        startup_logo = response.xpath('//div[@class="su-logo"]/a/img/@src').get()

        # add data
        data = []
        startup_country = response.xpath('//li[@class="su-country"]/a/div/text()').get().lower()
        startup_country = self.clean_text(startup_country)
        data.append({
            'data_type': self.settings.get('STARTUP_DATA_TYPE_REGION'),
            'data': startup_country,
        })

        startup_state = response.xpath('//li[@class="su-state"]/a/text()').get()
        startup_state = self.clean_text(startup_state)
        data.append({
            'data_type': self.settings.get('STARTUP_DATA_TYPE_CITY'),
            'data': startup_state,
        })

        startup_tags = response.xpath("//div[contains(@class, 'su-tags')]/descendant::li/a/text()").extract()
        data.append({
            'data_type': self.settings.get('STARTUP_DATA_TYPE_TAGS'),
            'data': startup_tags,
        })
        for people_row in response.xpath("//th[contains(text(),'%s')]/ancestor::table/tbody/tr" % 'Person'):
            people_name = people_row.xpath('./descendant::div[@class="name"]/a/text()').get()
            people_role = people_row.xpath('./td[@class="medium-content"][1]/text()').get()

            data.append({
                'data_type': self.settings.get('STARTUP_DATA_TYPE_PEOPLE'),
                'data': {
                    'name': self.clean_text(people_name),
                    'role': self.clean_text(people_role),
                }
            })

        # the visit page is redirected to the main startup page
        item_data = {
            'name': startup_name,
            'website': startup_website,
            'source_url': response.urljoin(response.url),
            'pitch': startup_pitch or '',
            'description': startup_description,
            'images': [startup_logo],
            'data': data,
        }
        yield scrapy.Request(
            url=response.urljoin(startup_website),
            callback=self.extract_startup_url,
            meta={'item_data': item_data}
        )

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
