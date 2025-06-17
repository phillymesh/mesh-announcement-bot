#! /bin/sh
docker build -t meshtastic .
docker run --restart unless-stopped -d --name meshtastic meshtastic