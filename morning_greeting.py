from datetime import datetime

import requests

from utils import sequencer, splitter


def morning_greeting() -> list[str]:
    """
    By default broadcasts to the whole mesh, but can broadcast to a specific address number if specified
    """
    print("Starting Morning Greeting")
    print(f"Today is {datetime.date(datetime.now()).isoformat()}")
    print("Fetching weather data")
    weatherdata = requests.get(
        "https://api.weather.gov/gridpoints/PHI/50,76/forecast"
    ).json()
    update_time = datetime.astimezone(
        datetime.fromisoformat(weatherdata["properties"]["updateTime"])
    )
    print("Time since forecast update:")
    print(datetime.astimezone(datetime.now()) - update_time)

    generate_time = datetime.astimezone(
        datetime.fromisoformat(weatherdata["properties"]["generatedAt"])
    )
    print("Time since forecast generated:")
    print(datetime.astimezone(datetime.now()) - generate_time)

    forecasts = weatherdata["properties"]["periods"]

    morning_greeting = "Good Morning Mesh from South Rittenhouse!"

    weather_messages = []
    for forecast in forecasts:
        weather_text = ""
        weather_text += forecast["name"]
        weather_text += "\n"
        weather_text += forecast["detailedForecast"]
        weather_messages.append(weather_text)

    messages = []
    messages += splitter(morning_greeting)
    messages += splitter(weather_messages[0])
    messages += splitter(weather_messages[1])
    packets = sequencer(messages)

    return packets


if __name__ == "__main__":  # allow for manual running
    for packet in morning_greeting():
        print(packet)
        print()
