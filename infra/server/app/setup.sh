#!/bin/bash

# start heartbeat in a subshell
#! the subshell sets an env var for itself, MAC is not in app.py
# (python3 heartbeat.py)
# sleep 1

# Create a znode for the service
# curl -X PUT http://zookeeper:2181/services/$ID -d "{'address': $MAC}"

echo "environment variable BR_BACKEND set to: $BR_BACKEND"
# echo "enp0s3 MAC: $enp0s3"

# mac address env var to be used in app.py
mac_address=$(ip link show eth0 | awk '/ether/ {print $2}')
export MAC=$mac_address

echo "MAC: $MAC"
echo "DISCOVERY_IP: $DISCOVERY_IP"

# until discovery is up
# sleep 1

# start app.py
exec "$@"