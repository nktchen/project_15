import requests

API_KEY = 'mqiZotA2vL62GqZwFlLA1p9UQG5jWlOg'

class WeatherModel:
    def __init__(self, api_key):
        self.API_KEY = api_key

    def get_location_key(self, city):
        try:
            url_location = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={self.API_KEY}&q={city}"
            response = requests.get(url_location)
            location_key = response.json()[0]['Key']
            return location_key
        except:
            return 'ПРОБЛЕМА С ГОРОДАМИ'

    def get_weather_data(self, location_key):
        try:
            url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={self.API_KEY}&details=true"
            response = requests.get(url)
            data = response.json()
            weather = {'is_precipitation': 'Да' if data[0]['HasPrecipitation'] else 'Нет',
                       'temperature': int(data[0]['Temperature']['Metric']['Value']),
                       'humidity': int(data[0]['RelativeHumidity']),
                       'wind': int(data[0]['Wind']['Speed']['Metric']['Value']),
                       }
            return weather
        except:
            return 'ПРОБЛЕМА ПРИ ОБРАЩЕНИИ К API'

    def weather_model(self, weather):
        switcher = {
            'precipitations': weather['is_precipitation'],
            'too hot': weather['temperature'] > 30,
            'too cold': weather['temperature'] < -10,
            'humidity': weather['humidity'] > 80,
            'wind' : weather['wind'] > 55,
        }
        if switcher['precipitations'] or switcher['too hot'] or switcher['too cold'] or switcher['humidity'] or switcher['wind']:
            return False  #True значит, что погода хорошая, False, что плохая
        else:
            return True

    def get_prediction(self, location_from, location_to):
        location_key_from = self.get_location_key(location_from)
        location_key_to = self.get_location_key(location_to)
        weather_from = self.get_weather_data(location_key_from)
        weather_to = self.get_weather_data(location_key_to)
        prediction_from = self.weather_model(weather_from)
        prediction_to = self.weather_model(weather_to)
        if prediction_from and prediction_to :
            return True #True значит, что погода хорошая, False, что плохая
        else:
            return False












