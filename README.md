# Meshtastic Announcement Bot

This program is designed to connect to a meshtastic node over WiFi and broadcast periodic announcements.
Written for and deployed in the [Philadelphia Mesh](https://phillymesh.net)

Current announcements:
- Every morning at 8:30AM, announce the weather forecaset from weather.gov for Philadelphia
- Every Saturday include a plug for the PhillyMesh/Philly Radio Discord
- Every Sunday include a list of upcoming mesh-related events
  - Event data is sourced from the Discord event calendar

## Installation/Deployment
Everything is designed to run in a docker container, but can be run directly in python after installing the necessary requirements

1. Clone this repository
2. Rename secrets.example.json to secrets.json and add necessary values
    - Node host is the IP address of your meshtastic node
    - Discord guild ID is the ID of your discord server 
    - You'll need to get a disord bot key from the developer portal, and add it to your discord server.
3. Change the code as needed to reflect the needs of your mesh (weather location, timezones, etc)
3. Build and start the image, or run the script directly

## Adding new announements
I'm using the [schedule](https://schedule.readthedocs.io/en/stable/) library to manage scheduling.

To create a new announcement, add a new schedule line to app.py, including a function that returns an array of strings (see discord_plug for a simple example).
Just make sure that each string is under the 200 character limit or else the packet will be too large to send.