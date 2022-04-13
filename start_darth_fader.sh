#!/bin/sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd home/measure_pi/darth_fader
python3 main.py >> /home/measure_pi/logs/fader_log.txt
cd /
