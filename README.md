# MeasurePi

A simple tool to help me keep track of where I am in a 'performance'. Displays bars, triplets, etc on a LaunchPad mini so I can hopefully time transitions a bit better.

## Raspberry Setup

I configured the Raspberry using the instructions Andrew Nicolaou wrote in his third Raspberry MIDI blog post: https://andrewnicolaou.co.uk/posts/2016/pi-zero-midi-3-two-things-at-once.

The Python script runs on boot with a crontab entry @reboot:
```sh
@reboot sh /home/pi/measure_pi/start_measure_pi.sh > /home/pi/measure_pi/logs/cronlog 2>&1
```
