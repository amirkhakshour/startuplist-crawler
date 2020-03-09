import re

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
