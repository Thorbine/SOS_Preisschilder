#!/bin/bash
cd "$(dirname "$0")"
python3 -m pip install -q --prefer-binary -r requirements.txt
python3 main.py || read -p "Fehler - Enter zum Beenden"
