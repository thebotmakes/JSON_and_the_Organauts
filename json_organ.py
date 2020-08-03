from pyowm import OWM
import time
import rtmidi
from papirus import PapirusTextPos

owm = OWM('44612535339ec837f25ff4b09b033791')  # You MUST provide a valid API key
mgr = owm.weather_manager()

text = PapirusTextPos()
text.AddText("loading...",5,0,Id ="line1")
text.AddText("please wait...",5,50,Id ="line2")

regions = {
  "Viking" : {"lat" : 59.65,"lon" : 02.00},
  "North Utsire" : {"lat": 60.00,"lon" : 04.68},
  "South Utsire" : {"lat" : 58.23,"lon" : 05.65},
  "Forties" : {"lat": 57.15,"lon" : 2.50},
  "Forth" : {"lat" : 56.20,"lon" : 1.55},
  "Cromarty" : {"lat" : 57.65,"lon" : -2.00},
  "Tyne" : {"lat" : 55.08,"lon" : -0.53},
  "Dogger" : {"lat" : 55.08,"lon" : 01.50},
  "Fisher" : {"lat" : 56.73,"lon" : 6.18},
  "German Bight" : {"lat" : 54.23,"lon" : 06.05},
  "Humber" : {"lat" : 53.30,"lon" : 02.10},
  "Thames" : {"lat" : 51.80,"lon" : 02.83},
  "Dover" : {"lat" : 50.65,"lon" : 01.35},
  "Wight" : {"lat" : 49.95,"lon" : -0.25},
  "Portland" : {"lat" : 49.43,"lon" : -2.43},
  "Plymouth" : {"lat" : 49.16,"lon" : -4.73}
}

names = []
for x, y in regions.items():
    names.append(x)
print(names)

def get_weather(station):
    w_list = []
    weather_at_station = mgr.weather_at_coords(regions[names[station]]['lat'],regions[names[station]]['lon']).weather
    wind = weather_at_station.wind()
    w_list.append(int(wind['speed']))
    w_list.append(int(wind['deg']))
    temp = weather_at_station.temperature('kelvin')
    w_list.append(int(temp['temp']))
    w_list.append(int(temp['feels_like']))
    w_list.append(int(weather_at_station.humidity))
    pressure = weather_at_station.pressure
    w_list.append(int(pressure['press']))
    return w_list

def midi_dictionary():
    midi_notes = []
    for i in range(73):
        midi_notes.append(i)
    musical_notes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    note_count = 0
    all_count = 0
    all_notes = []
    while all_count < 73:
        all_notes.append(musical_notes[note_count])
        note_count += 1
        all_count += 1
        if note_count >= 12:
            note_count = 0
    print(len(all_notes))
    midi_dict = dict(zip(midi_notes, all_notes))
    return midi_dict

def calc_scale():
    melodic_minor_list = [2, 1, 2, 2, 2, 2, 1]
    root_note = 2 #d
    notes = [root_note]
    scale_count = 0
    n = root_note
    while n < 71:
        n = n + melodic_minor_list[scale_count]
        notes.append(n)
        scale_count+=1
        if scale_count >= 7:
            scale_count = 0
    return notes

def midi_restrict(number_list):
    midi_w_list = [item % 72 for item in number_list]
    return midi_w_list

def fit_scale(midi_w_list):
    from bisect import bisect_left

    def take_closest(myList, myNumber):
        """
        Assumes myList is sorted. Returns closest value to myNumber.

        If two numbers are equally close, return the smallest number.
        """
        pos = bisect_left(myList, myNumber)
        if pos == 0:
            return myList[0]
        if pos == len(myList):
            return myList[-1]
        before = myList[pos - 1]
        after = myList[pos]
        if after - myNumber < myNumber - before:
           return after
        else:
           return before
    midi_final = []
    for note in midi_w_list:
        midi_final.append(take_closest(scale,note))
    note_names = []
    for note in midi_final:
        note_names.append(midi_dict.get(note))
    separator = ", "
    note_text = separator.join(note_names)
    return midi_final, note_names, note_text

def output_midi(station, midi_final):
    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()
    print("MIDI ports available:-")
    for i in range(0,len(available_ports)):
        print(i,available_ports[i])

    if available_ports:
        midiout.open_port(1)
    else:
        midiout.open_virtual_port("My virtual output")

    with midiout:

        text.UpdateText("line1",names[station])
        text.UpdateText("line2",note_text)
        for note in midi_final:
            note_on = [0x90, note, 112]
            midiout.send_message(note_on)
            time.sleep(5)
        time.sleep(10)
        for note in midi_final:
            note_off = [0x80, note, 0]
            midiout.send_message(note_off)
            time.sleep(1)
        time.sleep(0.1)

        del midiout

station = 0
while True:
    w_list = get_weather(station)
    midi_dict = midi_dictionary()
    scale = calc_scale()
    midi_w_list = midi_restrict(w_list)
    (midi_final, note_names, note_text) = fit_scale(midi_w_list)
    output_midi(station,midi_final)
    time.sleep(5)
    station += 1
    if station >= len(names):
        station = 0
