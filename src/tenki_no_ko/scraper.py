import requests
from bs4 import BeautifulSoup


class Scraper:
    def get_soup(self, url):
        try:
            content = requests.get(url).content
            return BeautifulSoup(content, 'html.parser')
        except requests.exceptions.RequestException:
            return None
