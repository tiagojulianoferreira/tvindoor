import requests

class APIWrapper:
    def __init__(self, openweathermap_api_key):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.openweathermap_api_key = openweathermap_api_key

    def get_weather_data(self, city):
        weather_url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': self.openweathermap_api_key,
            'units': 'metric'
        }

        response = requests.get(weather_url, params=params)

        if response.status_code == 200:
            weather_data = response.json()
            return weather_data
        else:
            return None
