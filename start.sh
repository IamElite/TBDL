#!/bin/bash

# Python virtual environment activate karein
source .venv/bin/activate

# Aria2c (xria) daemon ko background mein start karein
# --enable-rpc: RPC interface enable karein
# --rpc-listen-all=true: Sabhi network interfaces par listen karein (localhost se access ke liye zaroori)
# --rpc-listen-port=${ARIA2_PORT:-6800}: Environment variable ARIA2_PORT use karein, default 6800 agar set na ho
# --rpc-secret=${ARIA2_SECRET:-}: Environment variable ARIA2_SECRET use karein, default empty agar set na ho
# --rpc-allow-origin-all: Cross-origin requests allow karein (agar zaroorat ho)
# --daemon: Aria2c ko background process ke roop mein chalayein
# > /dev/null 2>&1: Aria2c ke output ko suppress karein (production ke liye accha)
# &: Command ko background mein run karein
echo "Starting xria (aria2c) daemon..."
nohup xria \
  --enable-rpc \
  --rpc-listen-all=true \
  --rpc-listen-port=${ARIA2_PORT:-6800} \
  --rpc-secret=${ARIA2_SECRET:-} \
  --rpc-allow-origin-all \
  --daemon \
  --max-tries=50 \
  --retry-wait=3 \
  --continue=true \
  --min-split-size=4M \
  --split=10 \
  --allow-overwrite=true > /dev/null 2>&1 &

# Aria2c RPC server ke start hone ka wait karein
echo "Waiting for xria (aria2c) RPC server to start..."
MAX_RETRIES=10 # Maximum attempts to check port (10 * 3 seconds = 30 seconds timeout)
RETRY_DELAY=3  # Delay between retries in seconds
CURRENT_RETRY=0

while [ ${CURRENT_RETRY} -lt ${MAX_RETRIES} ]; do
  # Check if the RPC port is open using netcat (nc)
  # -z: zero-I/O mode (just scan for listening daemons)
  # -w 1: 1 second timeout for the connection attempt
  if nc -z -w 1 localhost ${ARIA2_PORT:-6800}; then
    echo "xria (aria2c) RPC server is up and running!"
    break
  fi
  echo "xria (aria2c) not yet listening on port ${ARIA2_PORT:-6800}. Retrying in ${RETRY_DELAY} seconds..."
  sleep ${RETRY_DELAY}
  CURRENT_RETRY=$((CURRENT_RETRY + 1))
done

# Agar Aria2c start nahi hua toh error message print karein aur exit karein
if [ ${CURRENT_RETRY} -eq ${MAX_RETRIES} ]; then
  echo "Error: xria (aria2c) RPC server failed to start within the timeout. Exiting."
  exit 1
fi

# Python bot script run karein
echo "Starting Python bot..."
python3 terabox.py
