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

# Launchpad
COLOR_OFF = 0
COLOR_RED = 3
COLOR_GREEN = 48
COLOR_ORANGE = 51

BRIGHTNESS_DIM = 17
BRIGHTNESS_MEDIUM = 34
BRIGHTNESS_HIGH = 51

RESET = [176, 0, 0]

GRID = [
    [(144, 0), (144, 1), (144, 2), (144, 3), (144, 4), (144, 5), (144, 6), (144, 7)],
    [(144, 16), (144, 17), (144, 18), (144, 19), (144, 20), (144, 21), (144, 22), (144, 23)],
    [(144, 32), (144, 33), (144, 34), (144, 35), (144, 36), (144, 37), (144, 38), (144, 39)],
    [(144, 48), (144, 49), (144, 50), (144, 51), (144, 52), (144, 53), (144, 54), (144, 55)],
    [(144, 64), (144, 65), (144, 66), (144, 67), (144, 68), (144, 69), (144, 70), (144, 71)],
    [(144, 80), (144, 81), (144, 82), (144, 83), (144, 84), (144, 85), (144, 86), (144, 87)],
    [(144, 96), (144, 97), (144, 98), (144, 99), (144, 100), (144, 101), (144, 102), (144, 103)],
    [(144, 112), (144, 113), (144, 114), (144, 115), (144, 116), (144, 117), (144, 118), (144, 119)]
]

def grid(x, y):
    global GRID
    return GRID[x][y]

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
