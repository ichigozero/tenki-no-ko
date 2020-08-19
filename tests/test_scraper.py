import requests
from bs4 import BeautifulSoup

DUMMY_URL = 'http://localhost'


def test_get_soup(requests_mock, scraper, index_html):
    requests_mock.get(DUMMY_URL, content=index_html)
    soup = scraper.get_soup(DUMMY_URL)
    assert soup == BeautifulSoup(index_html, 'html.parser')


def test_failed_to_get_soup(requests_mock, scraper):
    requests_mock.get(DUMMY_URL, exc=requests.exceptions.HTTPError)
    soup = scraper.get_soup(DUMMY_URL)
    assert soup is None
