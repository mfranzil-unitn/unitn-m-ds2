#!/bin/bash

# Check that Reliable Broadcast works with Perfect Channels and No Crash Failures

echo "#######################################################"
echo "Testing Broadcast with Perfect Channels and No Failures"
echo "#######################################################"
sleep 3
python r_broadcast.py --lossP 0.0 --crashP 0.0


echo "#######################################################"
echo "Now with Fair Loss Channels and Crash Failures"
echo "#######################################################"
sleep 3
python r_broadcast.py --lossP 0.1 --crashP 0.01



echo "#######################################################"
echo "Now with SUPER LOSSY CHANNELS"
echo "#######################################################"
sleep 3
python r_broadcast.py --lossP 0.95 --crashP 0.01
