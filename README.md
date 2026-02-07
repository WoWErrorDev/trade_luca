# Trade Luca

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set secrets via environment variables:

```bash
export BINANCE_API_KEY=...
export BINANCE_API_SECRET=...
export TELEGRAM_TOKEN=...
export TELEGRAM_CHAT_ID=...
```

## Run

```bash
python -m app.main --mode paper --venue both
python -m app.main --mode live --venue binance
python -m app.main --mode paper --once
```
