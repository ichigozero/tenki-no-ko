from bs4 import BeautifulSoup


def test_extract_regions(mocker, index_html, location_scraper):
    mock_get_soup = mocker.patch.object(
        target=location_scraper,
        attribute='get_soup',
        return_value=BeautifulSoup(index_html, 'html.parser')
    )

    first_expected_value = {
        'id': '1',
        'region': '北海道地方'
    }
    last_expected_value = {
        'id': '10',
        'region': '沖縄地方'
    }
    output = location_scraper.extract_regions()

    mock_get_soup.called_once_with('https://tenki.jp')
    assert output[0] == first_expected_value
    assert output[-1] == last_expected_value


def test_extract_prefectures(mocker, prefecture_html, location_scraper):
    mock_get_soup = mocker.patch.object(
        target=location_scraper,
        attribute='get_soup',
        return_value=BeautifulSoup(prefecture_html, 'html.parser')
    )

    first_expected_value = {
        'id': '16',
        'region': '東京都'
    }
    last_expected_value = {
        'id': '23',
        'region': '長野県'
    }
    output = location_scraper.extract_prefectures(region_id=3)

    mock_get_soup.called_once_with('https://tenki.jp/forecast/3/')
    assert output[0] == first_expected_value
    assert output[-1] == last_expected_value
