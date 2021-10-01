#!/bin/bash

# Check the BEB works with Perfect Channels and No Crash Failures

echo "#######################################################"
echo "Testing Broadcast with Perfect Channels and No Failures"
echo "#######################################################"
sleep 3
python bebBroadcast.py --lossP 0.0 --crashP 0.0 --repP 1.0


echo "#######################################################"
echo "Now with Fair Loss Channels and Crash Failures"
echo "#######################################################"
sleep 3
python bebBroadcast.py --lossP 0.1 --crashP 0.01 --repP 0.1

