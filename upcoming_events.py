from utils import sequencer, max_length, splitter
from datetime import datetime, tzinfo
from zoneinfo import ZoneInfo
import requests
from secrets import guild_id, bot_token

# Time format: "%a %b %d %H:%M" -> Mon Jun 16 20:30

baseurl = "https://discord.com/api"

tz = ZoneInfo("America/New_York")


# get next week's events from discord added to
def upcoming_events() -> list[str]:
    print("Starting Event Calendar")
    r = r = requests.get(
        f"{baseurl}/guilds/{guild_id}/scheduled-events",
        headers={"Authorization": f"Bot {bot_token}"},
    )
    try:
        assert r.status_code == 200
    except AssertionError:
        print(f"API Error {r.status_code}")
        print(r.text)
        exit(1)
    # sort events by start time
    events = sorted(r.json(), key=lambda e: e["scheduled_start_time"])

    messages = []
    # initial message
    # "Upcoming Events for the week of Jun 17"
    today = (
        datetime.now().astimezone(tz).strftime("%b %d")
    )  # ensure it's EST no matter where deployed

    messages.append(f"Upcoming Events for the week of {today}")

    # message format:
    # Event name
    # Event start time (and optional end time)
    # Event Loation
    # Event details
    # truncate the whole thing to 190 characters
    # and add the sequencer

    for event in events:
        message = ""
        message += event["name"] + "\n"
        event_time = (
            datetime.fromisoformat(event["scheduled_start_time"])
            .astimezone(tz)
            .strftime("%a %b %H:%M")
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
        message += event["description"]

        # need to truncate to max_length chars
        messages.append(message[:max_length])
    # each event gets its own message
    # packets = sequencer(messages)

    # combine into one block of text and chunk from there
    packets = sequencer(splitter("\n\n".join(messages)))
    return packets


if __name__ == "__main__":  # allow for manual running
    for packet in upcoming_events():
        print(packet)
        print()
