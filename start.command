#!/bin/bash
cd "$(dirname "$0")"
python3 -m pip install -q -r requirements.txt
python3 main.py || read -p "Fehler - Enter zum Beenden"
