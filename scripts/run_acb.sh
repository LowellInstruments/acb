#!/usr/bin/env bash



FOL=/home/acbotics/acb



clear
echo


# grab this from our secure repository
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=



echo "activating python venv for ACB"
cd "$FOL" || (echo "ACB error, cannot switch folder to activate venv"; exit 1)
source .venv/bin/activate



# echo 'getting last ACB code'
# git pull



echo "running ACB"
cd $FOL || (echo "ACB error, cannot switch folder to run LIL"; exit 1)
python3 srv_main_gui.py
