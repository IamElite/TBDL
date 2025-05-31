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
# > /dev/null 2>&1: Aria2c ke output ko suppress karein
# &: Command ko background mein run karein
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

# Aria2c ko RPC server start karne ke liye thoda time dein
sleep 5

# Python bot script run karein
python3 terabox.py
