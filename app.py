import meshtastic
import meshtastic.tcp_interface
from utils import splitter, sequencer
import time, schedule, random
from datetime import datetime
from secrets import node_host
from morning_greeting import morning_greeting
from upcoming_events import upcoming_events

wait_time = 30  # time between each packet in seconds

# make everything modular to support more scheduling
# each function should return a collection of sequenced packets (text)


def discord_plug() -> list[str]:
    text = "Join the Philly Mesh Discord! https://discord.gg/MWWbAkRR9v"
    return splitter(discord_plug)


def send_packets(packets: list[str], dest: int | str = meshtastic.BROADCAST_ADDR):
    print("Connecting to node")
    with meshtastic.tcp_interface.TCPInterface(
        hostname=node_host
    ) as interface:  # automatically close when done/erroring
        # let's make sure the connection works first
        interface._waitConnected()
        print("Connected")
        if (
            dest == meshtastic.BROADCAST_ADDR
        ):  # sending broadcast, so add a random delay
            time.sleep(random.randint(0, 300))  # sleep for up to 5 minutes

        for packet in packets:
            time.sleep(wait_time)  # wait before sending the packet
            interface.sendText(packet, destinationId=dest, wantAck=True)
            print(packet)
            print()


schedule.every().day.at("08:30", "America/New_York").do(
    send_packets, packets=morning_greeting()
)
schedule.every().saturday.at("08:31", "America/New_York").do(
    send_packets, packets=discord_plug()
)
schedule.every().sunday.at("08:31", "America/New_York").do(
    send_packets, packets=upcoming_events()
)

if __name__ == "__main__":
    print("Starting server")
    while True:
        schedule.run_pending()
        # print(f"Remaining time until next: {format_time_left(schedule.idle_seconds())}")
        try:
            time.sleep(60)  # fire once a minute
        except KeyboardInterrupt:
            print("Exiting")
            exit()
