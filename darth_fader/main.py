import time
import sys
import rtmidi
from darth_fader import DarthFader

def main():
    # In- and output setup
    midi_in = rtmidi.MidiIn()
    midi_out = rtmidi.MidiOut()

    # midi_in.open_virtual_port("mvp")
    # print('MIDI in created')
    # f_midi is the port opened by the Raspberry midi gadget.
    for index, port in enumerate(midi_in.get_ports()):
        if 'f_midi' in port or 'Launch Control XL' == port:
            midi_in.open_port(index)
            print('MIDI in connected', port)

    # midi_out.open_virtual_port("mvp")
    # print('MIDI out created')
    for index, port in enumerate(midi_out.get_ports()):
        if 'f_midi' in port or 'Launch Control XL' == port:
            midi_out.open_port(index)
            print('MIDI out connected', port)

    instance = DarthFader(midi_in, midi_out)

    try:
        while True:
            # Just keep sleeping
            time.sleep(1)

    except KeyboardInterrupt:
        print('')

    finally:
        instance.done = True
        instance.kill()
        instance.join()
        del midi_in
        del midi_out

if __name__ == '__main__':
    sys.exit(main())
