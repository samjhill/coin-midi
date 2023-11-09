import os
import json
import time
import hmac
import hashlib
from threading import Thread
from midi import bitcoin_to_midi_note, get_midi_output, send_note_to_midi_output
from websocket import create_connection, WebSocketConnectionClosedException
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict
from statistics import mean

load_dotenv()
midi_out = None
maximum_amount = 0

def main():
    ws = None
    
    thread = None
    thread_running = False
    thread_keepalive = None

    midi_out = get_midi_output()

    def websocket_thread():
        global ws

        api_key = os.getenv("COINBASE_API_KEY")
        api_secret = os.getenv("COINBASE_API_SECRET")

        channel = "market_trades"
        timestamp = str(int(time.time()))
        product_ids = ["BTC-USD"]
        product_ids_str = ",".join(product_ids)
        message = f"{timestamp}{channel}{product_ids_str}"
        signature = hmac.new(api_secret.encode("utf-8"), message.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()

        ws = create_connection("wss://advanced-trade-ws.coinbase.com")
        ws.send(
            json.dumps(
                {
                    "type": "subscribe",
                    "product_ids": [
                        "BTC-USD",
                    ],
                    "channel": channel,
                    "api_key": api_key,
                    "timestamp": timestamp,
                    "signature": signature,
                }
            )
        )

        thread_keepalive.start()

        trade_buffer = defaultdict(list)
        current_second = int(time.time())
        
        while not thread_running:
            try:
                data = ws.recv()
                if data != "":
                    msg = json.loads(data)
                else:
                    msg = {}
            except ValueError as e:
                print(e)
                print("{} - data: {}".format(e, data))
            except Exception as e:
                print(e)
                print("{} - data: {}".format(e, data))
            else:
                if "events" in msg:
                    for event in msg["events"]:
                        if "trades" in event:
                            trades = event["trades"]
                            for trade in trades:
                                trade_time = datetime.fromisoformat(trade["time"])
                                trade_second = trade_time.second
                                trade_buffer[trade_second].append(trade)
                                
                                # Process trades for the previous second
                                while current_second != trade_second:
                                    process_trades(trade_buffer[current_second])
                                    current_second = (current_second + 1) % 60
                                    trade_buffer.pop(current_second, None)
                        
        try:
            if ws:
                ws.close()
        except WebSocketConnectionClosedException:
            pass
        finally:
            thread_keepalive.join()

    def websocket_keepalive(interval=30):
        global ws
        while ws.connected:
            ws.ping("keepalive")
            time.sleep(interval)

    def process_trades(trades):
        global maximum_amount
        # Process trades in the 1-second interval here
        if trades:
            print("Trades in 1-second interval:", json.dumps(trades, indent=2))
            average_price = mean(float(trade["price"]) for trade in trades)
            amount = sum(float(trade["size"]) for trade in trades)
            amount_of_buys = len(list(trade["side"] == "BUY" for trade in trades))
            amount_of_sells = len(list(trade["side"] == "SELL" for trade in trades))
            majority_side = "BUY" if amount_of_buys > amount_of_sells else "SELL"

            if amount > maximum_amount:
                maximum_amount = amount
            velocity = (amount / maximum_amount) * 100
            midi_note = bitcoin_to_midi_note(average_price, majority_side)
            send_note_to_midi_output(midi_note, midi_out, int(velocity))

    thread = Thread(target=websocket_thread)
    thread_keepalive = Thread(target=websocket_keepalive)
    thread.start()

    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Close the MIDI port when done
        midi_out.close()
