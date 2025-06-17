import meshtastic
import meshtastic.tcp_interface
from utils import splitter, sequencer
import requests
import time, schedule, random
from datetime import datetime

# sequence format: (x/y), so let's say 5 characters reserved
max_length = 200 - 5
wait_time = 30  # time between each packet in seconds
node_host = "10.0.0.222"


def morning_greeting(dest: int | str = meshtastic.BROADCAST_ADDR):
    """
    By default broadcasts to the whole mesh, but can broadcast to a specific address nuimber if specified
    """
    print("Starting Morning Greeting")
    print(f"Today is {datetime.date(datetime.now()).isoformat()}")
    if dest == meshtastic.BROADCAST_ADDR:  # sending broadcast, so add a random delay
        time.sleep(random.randint(0, 300))  # sleep for up to 5 minutes
    print("Fetching weather data")
    weatherdata = requests.get(
        "https://api.weather.gov/gridpoints/PHI/50,76/forecast"
    ).json()
    update_time = datetime.astimezone(datetime.fromisoformat(weatherdata['properties']['updateTime']))
    print("Time since forecast update:")
    print(datetime.astimezone(datetime.now())-update_time)

    generate_time = datetime.astimezone(datetime.fromisoformat(weatherdata['properties']['generatedAt']))
    print("Time since forecast generated:")
    print(datetime.astimezone(datetime.now())-generate_time)

    forecasts = weatherdata["properties"]["periods"]

    morning_greeting = "Good Morning Mesh from South Rittenhouse!"

    weather_messages = []
    for forecast in forecasts:
        weather_text = ""
        weather_text += forecast["name"]
        weather_text += "\n"
        weather_text += forecast["detailedForecast"]
        weather_messages.append(weather_text)

    discord_plug = "Join the Philly Mesh Discord! https://discord.gg/MWWbAkRR9v"

    messages = []
    messages += splitter(morning_greeting, max_length)
    messages += splitter(weather_messages[0], max_length)
    messages += splitter(weather_messages[1], max_length)

    # only add discord plug once a week on saturdays
    if datetime.weekday(datetime.now()) == 5:
        messages += splitter(discord_plug)

    packets = sequencer(messages)

    print("Connecting to node")
    with meshtastic.tcp_interface.TCPInterface(
        hostname=node_host
    ) as interface:  # automatically close when done/erroring
        # let's make sure the connection works first
        interface._waitConnected()
        print("Connected")
        for packet in packets:
            time.sleep(wait_time)  # wait before sending the packet
            interface.sendText(packet, destinationId=dest, wantAck=True)
            print(packet)
            print()


schedule.every().day.at("08:30", "America/New_York").do(morning_greeting)


def format_time_left(seconds_left):
    days, rem = divmod(seconds_left, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"


if __name__ == "__main__":  # allow for manual running
    print("Starting server")
    while True:
        schedule.run_pending()
        # print(f"Remaining time until next: {format_time_left(schedule.idle_seconds())}")
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("Exiting")
            exit()
