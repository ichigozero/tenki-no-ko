import os
import datetime

import pytest

from tenki_no_ko import LocationScraper
from tenki_no_ko import Scraper
from tenki_no_ko import WeatherScraper


def test_file(filename):
    path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'test_files',
    )
    with open(os.path.join(path, filename), 'r') as f:
        return f.read()


@pytest.fixture
def datetime_now_patch(monkeypatch):
    class MockDateTime(datetime.datetime):
        @classmethod
        def now(*args, **kwargs):
            return datetime.datetime(2020, 2, 29, 10, 0, 0)

    monkeypatch.setattr(datetime, 'datetime', MockDateTime)


@pytest.fixture(scope='module')
def index_html():
    return test_file('index.html').encode('utf-8')


@pytest.fixture(scope='module')
def prefecture_html():
    return test_file('prefecture.html').encode('utf-8')


@pytest.fixture(scope='module')
def subprefecture_html():
    return test_file('subprefecture.html').encode('utf-8')


@pytest.fixture(scope='module')
def forecast_summary_html():
    return test_file('forecast_summary.html').encode('utf-8')


@pytest.fixture(scope='module')
def three_hourly_forecast_html():
    return test_file('3_hourly_forecast.html').encode('utf-8')


@pytest.fixture
def scraper():
    return Scraper()


@pytest.fixture
def location_scraper(mocker):
    return LocationScraper()


@pytest.fixture
def weather_scraper(mocker):
    return WeatherScraper()
