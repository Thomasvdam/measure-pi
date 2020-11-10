import math
import rtmidi
from rtmidi.midiconstants import TIMING_CLOCK, SONG_START, SONG_CONTINUE, SONG_STOP

# In- and output setup
midi_in = rtmidi.MidiIn()
midi_out = rtmidi.MidiOut()

# f_midi is the port opened by the Raspberry midi gadget.
for index, port in enumerate(midi_in.get_ports()):
    if 'f_midi' in port:
        midi_in.open_port(index)

for index, port in enumerate(midi_out.get_ports()):
    if 'f_midi' in port:
        midi_out.open_port(index)

# Clock messages are ignored by default
midi_in.ignore_types(timing=False)

result = {
    TIMING_CLOCK: lambda x: x + 1,
    SONG_START: lambda x: 0,
}

# State
pulse_count = 0

def handle_input(event, data=None):
    message, deltatime = event
    if message[0] in [TIMING_CLOCK, SONG_START]:
        global pulse_count
        pulse_count = result.get(message[0])(pulse_count)
        update_lp()
    else:
        print(message)

midi_in.set_callback(handle_input)

# floor(pulse_count / 24) % 16
quarter_notes = [
    grid(0, 4), grid(1, 5), grid(2, 6), grid(3, 7),
    grid(4, 7), grid(5, 6), grid(6, 5), grid(7, 4),
    grid(7, 3), grid(6, 2), grid(5, 1), grid(4, 0),
    grid(3, 0), grid(2, 1), grid(1, 2), grid(0, 3)
]

# floor(pulse_count / 384) % 4
phrases = [
    grid(3, 4), grid(4, 4), grid(4, 3), grid(3, 3)
]

def update_lp():
    global pulse_count
    global quarter_notes
    global phrases
    q_note_count = math.floor(pulse_count / 24)
    active_q_note = q_note_count % 16
    if active_q_note == 0:
        for notes in quarter_notes:
            message = list(notes) + [COLOR_OFF]
            midi_out.send_message(message)
    else:
        prev_note_pad = list(quarter_notes[active_q_note - 1]) + [COLOR_ORANGE & BRIGHTNESS_DIM]
        midi_out.send_message(prev_note_pad)
    active_note_pad = list(quarter_notes[active_q_note]) + [COLOR_ORANGE & BRIGHTNESS_HIGH]
    midi_out.send_message(active_note_pad)
    p_part_count = math.floor(pulse_count / 384)
    active_phrase = p_part_count % 4
    if active_phrase == 0:
        for part in phrases:
            message = list(part) + [COLOR_OFF]
            midi_out.send_message(message)
    else:
        prev_part_pad = list(phrases[active_phrase - 1]) + [COLOR_GREEN & BRIGHTNESS_DIM]
        midi_out.send_message(prev_part_pad)
    active_part_pad = list(phrases[active_phrase]) + [COLOR_GREEN & BRIGHTNESS_HIGH]
    midi_out.send_message(active_part_pad)
