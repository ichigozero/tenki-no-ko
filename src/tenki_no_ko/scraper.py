import functools

import requests
from bs4 import BeautifulSoup


def _ignore_exceptions(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except AttributeError:
            return None

    return wrapper


class Scraper:
    def get_soup(self, url):
        try:
            content = requests.get(url).content
            return BeautifulSoup(content, 'html.parser')
        except requests.exceptions.RequestException:
            return None


class LocationScraper(Scraper):
    @_ignore_exceptions
    def extract_regions(self):
        regions = []
        soup = self.get_soup('https://tenki.jp')
        th_tags = (
            soup
            .find('table', class_='common-list-entries')
            .find_all('th')
        )

        for th_tag in th_tags:
            regions.append(
                {
                    'id': th_tag.a['href'].split('/')[-2],
                    'region': th_tag.get_text(strip=True)
                }
            )

        return regions

    @_ignore_exceptions
    def extract_prefectures(self, region_id):
        prefectures = []
        url = 'https://tenki.jp/forecast/{}/'.format(region_id)
        soup = self.get_soup(url)
        li_tags = (
            soup
            .find('table', class_='common-list-entries')
            .find('tr')
            .find_all('li')
        )

        for li_tag in li_tags:
            a_tag = li_tag.find('a', class_='pref-link')
            prefectures.append(
                {
                    'id': a_tag['href'].split('/')[-2],
                    'region': a_tag.get_text(strip=True)
                }
            )

        return prefectures
