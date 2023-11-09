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

# Function to fetch real-time Bitcoin buy and sell data
def get_realtime_bitcoin_data():
    url = f'https://api.pro.coinbase.com/products/{CRYPTO_PAIR}/ticker'
    response = requests.get(url)
    data = response.json()
    return data['price']

# Function to convert Bitcoin price to MIDI note
def bitcoin_to_midi_note(bitcoin_price):
    min_price = 10000  # Minimum Bitcoin price
    max_price = 60000  # Maximum Bitcoin price
    min_note = 60  # Lowest MIDI note (C4)
    max_note = 96  # Highest MIDI note (C6)
    
    # Scale the Bitcoin price to the MIDI note range
    note = int(((bitcoin_price - min_price) / (max_price - min_price)) * (max_note - min_note) + min_note)
    random_variation = random.randrange(0, 5)

    note = note + random_variation
    print(f"note: {note}")
    return note

# Main loop for real-time Bitcoin to MIDI conversion
while True:
    try:
        bitcoin_price = float(get_realtime_bitcoin_data())
        midi_note = bitcoin_to_midi_note(bitcoin_price)
        midi_output.send(mido.Message('note_on', note=midi_note, velocity=64))
        time.sleep(1)  # Adjust the frequency of MIDI updates as needed
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)  # Wait for a minute before retrying in case of an error

# Close the MIDI port when done
midi_output.close()
