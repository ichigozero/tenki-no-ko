from bs4 import BeautifulSoup


def test_extract_forecast_summary(
        mocker,
        forecast_summary_html,
        weather_scraper
):
    mock_get_soup = mocker.patch.object(
        target=weather_scraper,
        attribute='get_soup',
        return_value=BeautifulSoup(forecast_summary_html, 'html.parser')
    )
    location_ids = {
        'region_id': '3',
        'prefecture_id': '16',
        'subprefecture_id': '4410',
        'city_id': '13101'
    }
    output = weather_scraper.extract_forecast_summary(location_ids)

    mock_get_soup.assert_called_once_with(
        'https://tenki.jp/forecast/3/16/4410/13101/'
    )
    assert output == {
        'today': {
            'date': '08月20日(木)',
            'weather': '晴',
            'temps': {
                'high': '35℃ [+1]',
                'low': '28℃ [+1]',
            },
        },
        'tomorrow': {
            'date': '08月21日(金)',
            'weather': '晴',
            'temps': {
                'high':  '35℃ [0]',
                'low': '25℃ [-2]',
            },
        }
    }
