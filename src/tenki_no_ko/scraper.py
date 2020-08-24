import copy
import datetime
import functools
import re

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
        regions = {}
        soup = self.get_soup('https://tenki.jp')
        th_tags = (
            soup
            .find('table', class_='common-list-entries')
            .find_all('th')
        )

        for th_tag in th_tags:
            region_id = th_tag.a['href'].split('/')[-2]
            regions[region_id] = th_tag.get_text(strip=True)

        return regions

    @_ignore_exceptions
    def extract_prefectures(self, region_id):
        prefectures = {}
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
            prefecture_id = a_tag['href'].split('/')[-2]
            prefectures[prefecture_id] = a_tag.get_text(strip=True)

        return prefectures

    @_ignore_exceptions
    def extract_subprefectures_and_cities(self, region_id, prefecture_id):
        output = {}
        url = 'https://tenki.jp/forecast/{}/{}/'.format(
            region_id,
            prefecture_id
        )
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


class WeatherScraper(Scraper):
    def extract_forecast_summary(self, location_ids):
        def _extract_forecast_data(section_tag):
            try:
                date = re.search(
                    r'([0-9]+月[0-9]+日\([日|月|火|水|木|金|土]\))',
                    section_tag.h3.get_text(strip=True)
                ).group(1)
                weather = (
                    section_tag
                    .find('p', class_='weather-telop')
                    .get_text(strip=True)
                )
                highest_temperature = '{} {}'.format(
                    (
                        section_tag
                        .find('dd', class_='high-temp temp')
                        .get_text(strip=True)
                    ),
                    (
                        section_tag
                        .find('dd', class_='high-temp tempdiff')
                        .get_text(strip=True)
                    ),
                )
                lowest_temperature = '{} {}'.format(
                    (
                        section_tag
                        .find('dd', class_='low-temp temp')
                        .get_text(strip=True)
                    ),
                    (
                        section_tag
                        .find('dd', class_='low-temp tempdiff')
                        .get_text(strip=True)
                    ),
                )

                return {
                    'date': date,
                    'weather': weather,
                    'temps': {
                        'high': highest_temperature,
                        'low': lowest_temperature
                    },
                }
            except AttributeError:
                return {
                    'date': '',
                    'weather': '',
                    'temps': {
                        'high': '',
                        'low': ''
                    },
                }

        try:
            url = (
                'https://tenki.jp/forecast/'
                '{region_id}/{prefecture_id}/'
                '{subprefecture_id}/{city_id}/'
            ).format(
                region_id=location_ids.get('region_id'),
                prefecture_id=location_ids.get('prefecture_id'),
                subprefecture_id=location_ids.get('subprefecture_id'),
                city_id=location_ids.get('city_id')
            )

            soup = self.get_soup(url)

            h2_tag = soup.find('section', class_='section-wrap').h2
            update_datetime = (
                h2_tag
                .find('time', class_='date-time')
                .get_text(strip=True)
                .replace('発表', '')
            )

            # Prevent the original tree from being modified
            # when calling extract() method
            h2_tag_copy = copy.copy(h2_tag)
            h2_tag_copy.time.extract()
            city = h2_tag_copy.get_text(strip=True).replace('の天気', '')

            today_section = soup.find('section', class_='today-weather')
            tomorrow_section = soup.find('section', class_='tomorrow-weather')
        except AttributeError:
            city = ''
            update_datetime = ''
            today_section = None
            tomorrow_section = None

        return {
            'city': city,
            'update_datetime': update_datetime,
            'forecasts': {
                'today': _extract_forecast_data(today_section),
                'tomorrow': _extract_forecast_data(tomorrow_section)
            }
        }

    def extract_3_hourly_forecasts(self, location_ids):
        def _extract_forecast_data(soup, table_id):
            forecasts = []

            try:
                table = soup.find('table', id='forecast-point-3h-today')
                hours = (
                    table
                    .find('tr', class_='hour')
                    .find_all('td')
                )
                weathers = (
                    table
                    .find('tr', class_='weather')
                    .find_all('td')
                )
                temperatures = (
                    table
                    .find('tr', class_='temperature')
                    .find_all('td')
                )

                for index, hour in enumerate(hours):
                    forecasts.append({
                        'hour': hours[index].get_text(strip=True),
                        'weather': weathers[index].get_text(strip=True),
                        'temp': temperatures[index].get_text(strip=True),
                    })
            except AttributeError:
                START_HOUR = 3
                HOURS_IN_A_DAY = 24
                INTERVAL = 3

                for hour in range(
                        START_HOUR,
                        HOURS_IN_A_DAY + INTERVAL,
                        INTERVAL
                ):
                    forecasts.append({
                        'hour': str(hour).zfill(2),
                        'weather': '',
                        'temp': '',
                    })

            return forecasts

        try:
            url = (
                'https://tenki.jp/forecast/'
                '{region_id}/{prefecture_id}/'
                '{subprefecture_id}/{city_id}/'
                '3hours.html'
            ).format(
                region_id=location_ids.get('region_id'),
                prefecture_id=location_ids.get('prefecture_id'),
                subprefecture_id=location_ids.get('subprefecture_id'),
                city_id=location_ids.get('city_id')
            )
            soup = self.get_soup(url)
        except AttributeError:
            soup = None

        return {
            'today': _extract_forecast_data(
                soup=soup,
                table_id='forecast-point-3h-today'
            ),
            'tomorrow': _extract_forecast_data(
                soup=soup,
                table_id='forecast-point-3h-tomorrow'
            )
        }

    def extract_3_hourly_forecasts_for_next_24_hours(self, location_ids):
        INTERVAL = 3
        raw_forecasts = self.extract_3_hourly_forecasts(location_ids)

        sequence = int(datetime.datetime.now().hour / INTERVAL)
        today_forecasts = raw_forecasts['today']
        tomorrow_forecasts = raw_forecasts['tomorrow']

        forecasts = []
        forecasts.extend(today_forecasts[sequence:])
        forecasts.extend(tomorrow_forecasts[:sequence])

        return forecasts
