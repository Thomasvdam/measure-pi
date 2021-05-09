import time
import sequency
import sys
import rtmidi

def main():
    # In- and output setup
    midi_in = rtmidi.MidiIn()
    midi_out = rtmidi.MidiOut()

    # f_midi is the port opened by the Raspberry midi gadget.
    for index, port in enumerate(midi_in.get_ports()):
        if 'f_midi' in port:
            midi_in.open_port(index)
            print('MIDI in connected')

    for index, port in enumerate(midi_out.get_ports()):
        if 'f_midi' in port:
            midi_out.open_port(index)
            print('MIDI out connected')

    instance = sequency.Sequency(midi_in, midi_out)

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
