from bs4 import BeautifulSoup


def test_extract_regions(mocker, index_html, location_scraper):
    mock_get_soup = mocker.patch.object(
        target=location_scraper,
        attribute='get_soup',
        return_value=BeautifulSoup(index_html, 'html.parser')
    )
    output = location_scraper.extract_regions()

    mock_get_soup.assert_called_once_with('https://tenki.jp')
    assert output['1'] == '北海道地方'
    assert output['10'] == '沖縄地方'


def test_extract_prefectures(mocker, prefecture_html, location_scraper):
    mock_get_soup = mocker.patch.object(
        target=location_scraper,
        attribute='get_soup',
        return_value=BeautifulSoup(prefecture_html, 'html.parser')
    )
    output = location_scraper.extract_prefectures(region_id=3)

    mock_get_soup.assert_called_once_with('https://tenki.jp/forecast/3/')
    assert output['16'] == '東京都'
    assert output['23'] == '長野県'


def test_extract_subprefectures_and_cities(
        mocker,
        subprefecture_html,
        location_scraper
):
    mock_get_soup = mocker.patch.object(
        target=location_scraper,
        attribute='get_soup',
        return_value=BeautifulSoup(subprefecture_html, 'html.parser')
    )

    expected_value_1 = {
        'subprefecture_id': '4410',
        'city_name': '千代田区'
    }
    expected_value_2 = {
        'subprefecture_id': '4440',
        'city_name': '小笠原村'
    }
    output = location_scraper.extract_subprefectures_and_cities(
        region_id=3,
        prefecture_id=16
    )

    mock_get_soup.assert_called_once_with('https://tenki.jp/forecast/3/16/')
    assert output['東京23区']['13101'] == expected_value_1
    assert output['小笠原諸島(父島)']['13421'] == expected_value_2
