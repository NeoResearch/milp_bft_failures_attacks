#!/usr/bin/env bash
sudo apt-get install -y python3-venv
mkdir -p venv
cd venv
python3 -m venv env

source venv/env/bin/activate
pip3 install -r requirements.txt
sudo apt-get install python3-lxml
