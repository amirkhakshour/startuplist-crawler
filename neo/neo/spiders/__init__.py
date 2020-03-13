# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import re
from neo.utils import email_regex
from urllib.parse import urlparse, urljoin


class ExplorerSpiderMixin:
    def get_emails_from_response(self, response):
        text = response.body.decode('utf-8')
        """Returns an iterator of matched emails found in string s."""
        # Removing lines that start with '//' because the regular expression
        # mistakenly matches patterns like 'http://foo@bar.com' as '//foo@bar.com'.
        return set([email[0] for email in re.findall(email_regex, text)
                    if not (email[0].startswith('//') or '/' in email[0])])

    def clean_text(self, text):  # todo add Open/Closed principle
        if not text:
            return
        return text \
            .replace('/n', '') \
            .lower() \
            .strip()

    def get_base_url(self, url):
        url = urljoin(url, urlparse(url).path)
        return url.split('?')[0]
