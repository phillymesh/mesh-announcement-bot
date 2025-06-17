import meshtastic
import meshtastic.tcp_interface
from utils import splitter, sequencer
import requests
import time, schedule, random

# sequence format: (x/y), so let's say 5 characters reserved
max_length = 200 - 5
wait_time = 30  # time between each packet in seconds
node_host = "10.0.0.222"

print("Starting server")

def morning_greeting():
    print("Starting Morning Greeting")
    time.sleep(random.randint(0,300)) # sleep for a random time, up to 5 minutes
    weatherdata = requests.get(
        "https://api.weather.gov/gridpoints/PHI/50,76/forecast"
    ).json()
    forecasts = weatherdata["properties"]["periods"]

    morning_greeting = "Good Morning Mesh from South Rittenhouse!"

    weather_messages = []
    for forecast in forecasts:
        weather_text = ""
        weather_text += forecast["name"]
        weather_text += "\n"
        weather_text += forecast["detailedForecast"]
        weather_messages.append(weather_text)

    discord_plug = "Join the Philly Mesh Discord! https://discord.gg/hKCdVNuxFR"

    messages = []
    messages += splitter(morning_greeting, max_length)
    messages += splitter(weather_messages[0], max_length)
    messages += splitter(weather_messages[1], max_length)
    messages += splitter(discord_plug)

    packets = sequencer(messages)

    with meshtastic.tcp_interface.TCPInterface(hostname=node_host) as interface: # automatically close when done/erroring
        # let's make sure the connection works first
        interface._waitConnected()
        for packet in packets:
            interface.sendText(packet, channelIndex=0, wantAck=True)
            print(packet)
            print()
            # print("Sleeping to avoid flooding the net")
            time.sleep(wait_time)  # wait before sending next packet


schedule.every().day.at("08:30", "America/New_York").do(morning_greeting)


def format_time_left(seconds_left):
    days, rem = divmod(seconds_left, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"

if __name__ == "__main__": # allow for manual running
    while True:
        schedule.run_pending()
        # print(f"Remaining time until next: {format_time_left(schedule.idle_seconds())}")
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("Exiting")
            exit()
