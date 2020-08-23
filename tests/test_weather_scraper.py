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
        'city': '千代田区',
        'update_datetime': '20日06:00',
        'forecasts': {
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
        },
    }


def test_extract_3_hourly_forecasts(
    mocker,
    three_hourly_forecast_html,
    weather_scraper
):
    mock_get_soup = mocker.patch.object(
        target=weather_scraper,
        attribute='get_soup',
        return_value=BeautifulSoup(three_hourly_forecast_html, 'html.parser')
    )
    location_ids = {
        'region_id': '3',
        'prefecture_id': '16',
        'subprefecture_id': '4410',
        'city_id': '13101'
    }
    output = weather_scraper.extract_3_hourly_forecasts(location_ids)

    mock_get_soup.assert_called_once_with(
        'https://tenki.jp/forecast/3/16/4410/13101/3hours.html'
    )
    assert output == {
        'today': [
            {'hour': '03', 'weather': '晴れ', 'temp': '28.0'},
            {'hour': '06', 'weather': '晴れ', 'temp': '28.0'},
            {'hour': '09', 'weather': '晴れ', 'temp': '31.5'},
            {'hour': '12', 'weather': '晴れ', 'temp': '34.7'},
            {'hour': '15', 'weather': '晴れ', 'temp': '34.8'},
            {'hour': '18', 'weather': '晴れ', 'temp': '30.6'},
            {'hour': '21', 'weather': '晴れ', 'temp': '28.1'},
            {'hour': '24', 'weather': '晴れ', 'temp': '27.3'},
        ],
        'tomorrow': [
            {'hour': '03', 'weather': '晴れ', 'temp': '28.0'},
            {'hour': '06', 'weather': '晴れ', 'temp': '28.0'},
            {'hour': '09', 'weather': '晴れ', 'temp': '31.5'},
            {'hour': '12', 'weather': '晴れ', 'temp': '34.7'},
            {'hour': '15', 'weather': '晴れ', 'temp': '34.8'},
            {'hour': '18', 'weather': '晴れ', 'temp': '30.6'},
            {'hour': '21', 'weather': '晴れ', 'temp': '28.1'},
            {'hour': '24', 'weather': '晴れ', 'temp': '27.3'},
        ]
    }


def test_failed_to_extract_3_hourly_forecasts(
    mocker,
    weather_scraper
):
    mock_get_soup = mocker.patch.object(
        target=weather_scraper,
        attribute='get_soup',
        return_value=None
    )
    location_ids = {
        'region_id': '3',
        'prefecture_id': '16',
        'subprefecture_id': '4410',
        'city_id': '13101'
    }
    output = weather_scraper.extract_3_hourly_forecasts(location_ids)

    mock_get_soup.assert_called_once_with(
        'https://tenki.jp/forecast/3/16/4410/13101/3hours.html'
    )
    assert output == {
        'today': [
            {'hour': '03', 'weather': '', 'temp': ''},
            {'hour': '06', 'weather': '', 'temp': ''},
            {'hour': '09', 'weather': '', 'temp': ''},
            {'hour': '12', 'weather': '', 'temp': ''},
            {'hour': '15', 'weather': '', 'temp': ''},
            {'hour': '18', 'weather': '', 'temp': ''},
            {'hour': '21', 'weather': '', 'temp': ''},
            {'hour': '24', 'weather': '', 'temp': ''},
        ],
        'tomorrow': [
            {'hour': '03', 'weather': '', 'temp': ''},
            {'hour': '06', 'weather': '', 'temp': ''},
            {'hour': '09', 'weather': '', 'temp': ''},
            {'hour': '12', 'weather': '', 'temp': ''},
            {'hour': '15', 'weather': '', 'temp': ''},
            {'hour': '18', 'weather': '', 'temp': ''},
            {'hour': '21', 'weather': '', 'temp': ''},
            {'hour': '24', 'weather': '', 'temp': ''},
        ]
    }


def test_extract_3_hourly_forecasts_for_next_24_hours(
    mocker,
    datetime_now_patch,
    three_hourly_forecast_html,
    weather_scraper
):
    mock_get_soup = mocker.patch.object(
        target=weather_scraper,
        attribute='get_soup',
        return_value=BeautifulSoup(three_hourly_forecast_html, 'html.parser')
    )
    location_ids = {
        'region_id': '3',
        'prefecture_id': '16',
        'subprefecture_id': '4410',
        'city_id': '13101'
    }
    output = (
        weather_scraper
        .extract_3_hourly_forecasts_for_next_24_hours(location_ids)
    )

    mock_get_soup.assert_called_once_with(
        'https://tenki.jp/forecast/3/16/4410/13101/3hours.html'
    )
    assert output == [
        {'hour': '12', 'weather': '晴れ', 'temp': '34.7'},
        {'hour': '15', 'weather': '晴れ', 'temp': '34.8'},
        {'hour': '18', 'weather': '晴れ', 'temp': '30.6'},
        {'hour': '21', 'weather': '晴れ', 'temp': '28.1'},
        {'hour': '24', 'weather': '晴れ', 'temp': '27.3'},
        {'hour': '03', 'weather': '晴れ', 'temp': '28.0'},
        {'hour': '06', 'weather': '晴れ', 'temp': '28.0'},
        {'hour': '09', 'weather': '晴れ', 'temp': '31.5'},
    ]
