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

    def extract_subprefectures_and_cities(self, region_id, prefecture_id):
        output = {}
        url = 'https://tenki.jp/forecast/{}/'.format(region_id)
        soup = self.get_soup(url)
        h4_tags = (
            soup.
            find_all('h4', class_='forecast-point-city-name')
        )
        for h4_tag in h4_tags:
            # Since subprefecture_id are not really unique,
            # subprefecture_name is used as dictionary key instead.
            subprefecture_name = h4_tag.get_text(strip=True)
            output[subprefecture_name] = {}
            li_tags = h4_tag.find_next().find_all('li')

            for li_tag in li_tags:
                splitted_url = li_tag.a['href'].split('/')
                city_id = splitted_url[-2]
                subprefecture_id = splitted_url[-3]

                output[subprefecture_name][city_id] = {
                        'subprefecture_id': subprefecture_id,
                        'city_name': li_tag.a.get_text(strip=True)
                }

        return output
