#!/usr/bin/env bash


clear
echo

if [ $# -ne 1 ]; then echo "error, wrong number of parameters"; exit 1; fi


echo "unmanaging interface $1"
sudo nmcli dev set $1 managed no
rv=$?


if [ $rv -ne 0 ]; then echo "error unmanaging interface $1"; exit 1; fi

