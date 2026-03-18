#!/usr/bin/bash
# to be run in adhoc server

sudo ifconfig wlan0 down
sudo iwconfig wlan0 channel 1
sudo iwconfig wlan0 mode ad-hoc
sudo iwconfig wlan0 essid "MYADHOC"
#sudo iwconfig wlan0 key 1234567890
sudo ifconfig wlan0 192.168.9.2/24
sudo ifconfig wlan0 up
