import json
import urllib.request

API = "https://api.example.invalid/weather?city={city}"


def fetch_weather(city):
    with urllib.request.urlopen(API.format(city=city)) as resp:
        return json.load(resp)


def describe(city):
    data = fetch_weather(city)
    return f"{city}: {data['temp']}°C, {data['summary']}"
