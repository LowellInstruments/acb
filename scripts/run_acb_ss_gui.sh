#!/usr/bin/env bash



BLUE='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'


FOL=/home/pi/li/acb_ss_gui




clear
echo;



echo -e "\n${BLUE}ACB_SS_GUI: activate virtual environment${NC}"
cd $FOL || (echo -e "${RED}ACB_SS_GUI error, cannot switch folder${NC}"; exit 1)
source .venv/bin/activate



#echo -e "\n${BLUE}ACB_SS_GUI: upgrade PIP${NC}"
#pip install -q --upgrade pip



echo -e "\n${BLUE}ACB_SS_GUI: update itself${NC}"
cd $FOL && git reset --hard > /dev/null && git pull > /dev/null



echo -e "\n${BLUE}ACB_SS_GUI: run${NC}"
cd $FOL && python3 acb_ss_gui.py
