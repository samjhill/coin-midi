# coin-midi

Controls MIDI devices based on live cryptocurrency trade data from Coinbase!

[Makes..."music".](https://www.youtube.com/watch?v=EI-a79RqOVg)


## Setup

Clone this repo, and in your terminal, get into the directory:
```shell
git clone git@github.com:samjhill/coin-midi.git && cd coin-midi
```

Then, add a `.env` file in the root of the project with these settings:

```shell
COINBASE_API_KEY=
COINBASE_API_SECRET=
CRYPTO_PAIR=BTC-USD
```

## Running it

```shell
python3 -m main
```