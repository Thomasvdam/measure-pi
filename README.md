# MeasurePi

A simple tool to help me keep track of where I am in a 'performance'. Displays bars, triplets, etc on a LaunchPad mini so I can hopefully time transitions a bit better.

## Raspberry Setup

### First attempt at gadget

I configured the Raspberry using the instructions Andrew Nicolaou wrote in his third Raspberry MIDI blog post: https://andrewnicolaou.co.uk/posts/2016/pi-zero-midi-3-two-things-at-once.

### Second attempt at gadget

As the first attempt got me into issues with my MIDI USB host as the Pi also turned on host mode (I suspect because of the ether config), I'm trying something new and silly by changing the /boot/cmdline.txt file with a certain button combination. This will hopefully allow me to toggle between g_midi and g_ether without having to pop out the sd card. Fingers crossed.

### Python script on boot

The Python script runs on boot with a crontab entry @reboot:
```sh
@reboot sh /home/pi/measure_pi/start_measure_pi.sh > /home/pi/measure_pi/logs/cronlog 2>&1
```

