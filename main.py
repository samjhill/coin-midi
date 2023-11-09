import os
import time
import mido
import requests
from dotenv import load_dotenv
import random

load_dotenv()

# Define your Coinbase Pro API credentials
COINBASE_API_KEY = os.getenv("COINBASE_API_KEY")
COINBASE_API_SECRET = os.getenv("COINBASE_API_SECRET")

# Define the MIDI port for output
MIDI_PORT_NAME = os.getenv("MIDI_PORT_NAME")  # Use mido.get_output_names() to list available ports

# Initialize the MIDI output
print("Available midi outputs:")
for port in mido.get_output_names():
    print(port)

default_midi_port = mido.get_output_names().pop()
selected_midi_port = MIDI_PORT_NAME if MIDI_PORT_NAME else default_midi_port
midi_output = mido.open_output(selected_midi_port)
print(f"selected midi port: {selected_midi_port}")

# Define the cryptocurrency pair to monitor
CRYPTO_PAIR = os.getenv("CRYPTO_PAIR")

# Define the musical scales
scales = {
    "C Major": [0, 2, 4, 5, 7, 9, 11],  # C, D, E, F, G, A, B
    "C Natural Minor": [0, 2, 3, 5, 7, 8, 10],  # C, D, D#, F, G, G#, A#
    "C# Major": [1, 3, 5, 6, 8, 10, 0],  # C#, D#, F, F#, G#, A#, C
    "C# Natural Minor": [1, 3, 4, 6, 8, 9, 11],  # C#, D#, E, F#, G#, A, B
    "D Major": [2, 4, 6, 7, 9, 11, 1],  # D, E, F#, G, A, B, C#
    "D Natural Minor": [2, 4, 5, 7, 9, 10, 0],  # D, E, F, G, A, Bb, C
    "D# Major": [3, 5, 7, 8, 10, 0, 2],  # D#, F, G, G#, A#, C, D
    "D# Natural Minor": [3, 5, 6, 8, 10, 11, 1],  # D#, F, F#, G#, A#, B, C#
    "E Major": [4, 6, 8, 9, 11, 1, 3],  # E, F#, G#, A, B, C#, D#
    "E Natural Minor": [4, 6, 7, 9, 11, 0, 2],  # E, F#, G, A, B, C, D
    "F Major": [5, 7, 9, 10, 0, 2, 4],  # F, G, A, A#, C, D, E
    "F Natural Minor": [5, 7, 8, 10, 0, 1, 3],  # F, G, Ab, A#, C, Db, E
    "F# Major": [6, 8, 10, 11, 1, 3, 5],  # F#, G#, A#, B, C#, D#, F
    "F# Natural Minor": [6, 8, 9, 11, 1, 2, 4],  # F#, G#, A, B, C#, D, E
    "G Major": [7, 9, 11, 0, 2, 4, 6],  # G, A, B, C, D, E, F#
    "G Natural Minor": [7, 9, 10, 0, 2, 3, 5],  # G, A, Bb, C, D, Eb, F
    "G# Major": [8, 10, 0, 1, 3, 5, 7],  # G#, A#, B, C#, D#, E#, G
    "G# Natural Minor": [8, 10, 11, 1, 3, 4, 6],  # G#, A#, B, C#, D#, E, F#
    "A Major": [9, 11, 1, 2, 4, 6, 8],  # A, B, C#, D, E, F#, G#
    "A Natural Minor": [9, 11, 0, 2, 4, 5, 7],  # A, B, C, D, E, F, G
    "A# Major": [10, 0, 2, 3, 5, 7, 9],  # A#, B, C#, D#, E#, F#, G#
    "A# Natural Minor": [10, 0, 1, 3, 5, 6, 8],  # A#, B, C, D#, E#, F, G#
    "B Major": [11, 1, 3, 4, 6, 8, 10],  # B, C#, D#, E, F#, G#, A#
    "B Natural Minor": [11, 1, 2, 4, 6, 7, 9],  # B, C#, D, E, F#, G, A
}


selected_scale = os.getenv("MUSICAL_SCALE", "C Major")  # Default to C Major

# Function to fetch real-time Bitcoin buy and sell data
def get_realtime_bitcoin_data():
    url = f'https://api.pro.coinbase.com/products/{CRYPTO_PAIR}/ticker'
    response = requests.get(url)
    data = response.json()
    return data['price']

# Function to convert Bitcoin price to MIDI note
def bitcoin_to_midi_note(bitcoin_price, scale):
    min_price = 10000  # Minimum Bitcoin price
    max_price = 60000  # Maximum Bitcoin price
    min_note = 60  # Lowest MIDI note (C4)

    # Define the selected scale
    selected_scale_notes = scales[scale]

    # Calculate the range of notes within the selected scale
    note_range = len(selected_scale_notes)

    # Scale the Bitcoin price to the note range
    bitcoin_normalized = (bitcoin_price - min_price) / (max_price - min_price)

    # add some randomness for auditory niceness
    random_variation = random.randrange(0, 2)

    # Map the Bitcoin value to a note in the selected scale
    note_index = int(bitcoin_normalized * note_range) + random_variation

    # Add the note index to the base note (C4)
    note = min_note + selected_scale_notes[note_index]

    note = note + random_variation

    print(f"note: {note}")
    return note

# Get the configurable BPM (beats per minute)
BPM = int(os.getenv("BPM", 120))  # Default BPM is 120

# Calculate the sleep duration based on BPM
sleep_duration = 60 / BPM

# Main loop for real-time Bitcoin to MIDI conversion
while True:
    try:
        bitcoin_price = float(get_realtime_bitcoin_data())
        midi_note = bitcoin_to_midi_note(bitcoin_price, selected_scale)
        midi_output.send(mido.Message('note_on', note=midi_note, velocity=64))
        time.sleep(sleep_duration)  # Adjust the frequency of MIDI updates as needed
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)  # Wait for a minute before retrying in case of an error

# Close the MIDI port when done
midi_output.close()
