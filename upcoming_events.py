from datetime import datetime, timedelta
from urllib.parse import unquote
from zoneinfo import ZoneInfo

import requests

from utils import max_length, secrets, sequencer

# Time format: "%a %b %d %H:%M" -> Mon Jun 16 20:30

baseurl = "https://discord.com/api"

tz = ZoneInfo("America/New_York")


# get next week's events from discord added to
def upcoming_events() -> list[str]:
    print("Starting Event Calendar")
    print()
    messages = []
    # initial message
    # "Upcoming Events for the week of Jun 17"
    today = datetime.now().astimezone(tz)  # ensure it's EST no matter where deployed
    messages.append(f"Upcoming Events for the week of {today.strftime('%b %d')}:\n")

    r = requests.get(
        f"{baseurl}/guilds/{secrets['guild_id']}/scheduled-events",
        headers={"Authorization": f"Bot {secrets['bot_token']}"},
    )
    try:
        assert r.status_code == 200
    except AssertionError:
        print(f"API Error {r.status_code}")
        print(r.text)
        exit(1)

    events = r.json()

    # only include those in the next 7 days
    end_of_week = today + timedelta(days=7)
    events = filter(
        lambda e: datetime.fromisoformat(e["scheduled_start_time"]).astimezone(tz)
        < end_of_week,
        events,
    )

    # sort events by start time
    events = sorted(events, key=lambda e: e["scheduled_start_time"])

    print(f"Number of events: {len(events)}")
    if not events:
        # don't send anything
        return []

    # message format:
    # Event name
    # Event start time (and optional end time)
    # Event Location
    # Event details
    # truncate the whole thing to 190 characters
    # and add the sequencer

    for event in events:
        message = ""
        message += event["name"] + "\n"
        event_time = (
            datetime.fromisoformat(event["scheduled_start_time"])
            .astimezone(tz)
            .strftime("%a %b %d %H:%M")
        )  # start date and time
        if event.get("scheduled_end_time"):  # end time exists
            event_time += "-"
            event_time += (
                datetime.fromisoformat(event["scheduled_end_time"])
                .astimezone(tz)
                .strftime("%H:%M")
            )
        message += event_time + "\n"
        if event["entity_metadata"].get("location"):  # Manual location data
            message += event["entity_metadata"].get("location") + "\n"
        else:  # must be online
            message += "PRM Discord\n"
        message += unquote(event["description"])

        # need to truncate to max_length chars
        messages.append(message[:max_length])

    chunks = []
    current_string = ""
    while messages:  # still remaining info
        next_message = messages.pop(0)
        if len(current_string + next_message) < max_length:
            current_string += next_message
        else:
            chunks.append(current_string)
            current_string = next_message
    chunks.append(current_string)  # add last string
    packets = sequencer(chunks)
    return packets


if __name__ == "__main__":  # allow for manual running
    for packet in upcoming_events():
        print(packet)
        # print(f"{len(packet)} characters")
        print()
