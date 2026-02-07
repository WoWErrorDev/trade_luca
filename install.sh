#!/usr/bin/env bash
set -euo pipefail

APP_USER="trader"
APP_DIR="/opt/autotrader"
REPO_URL="https://github.com/tuo/repo.git" # <-- sostituisci con il tuo repo
BRANCH="${BRANCH:-main}"
PY_VER="3.11"

echo "[1/10] Update + pacchetti base"
sudo apt-get update -y
sudo apt-get install -y git curl ca-certificates ufw sqlite3 build-essential software-properties-common

echo "[2/10] Python ${PY_VER} (deadsnakes) + venv"
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update -y
sudo apt-get install -y python${PY_VER} python${PY_VER}-venv python${PY_VER}-dev

echo "[3/10] Utente dedicato"
if ! id "${APP_USER}" >/dev/null 2>&1; then
  sudo useradd -m -s /bin/bash "${APP_USER}"
fi

echo "[4/10] Directory applicazione"
sudo mkdir -p "${APP_DIR}"
sudo chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"

echo "[5/10] Clone/Update repo"
sudo -u "${APP_USER}" bash -lc "
set -e
if [ ! -d '${APP_DIR}/.git' ]; then
  git clone --branch '${BRANCH}' '${REPO_URL}' '${APP_DIR}'
else
  cd '${APP_DIR}'
  git fetch --all
  git reset --hard 'origin/${BRANCH}'
fi
"

echo "[6/10] Virtualenv + requirements"
sudo -u "${APP_USER}" bash -lc "
set -e
cd '${APP_DIR}'
python${PY_VER} -m venv .venv
source .venv/bin/activate
pip install -U pip wheel
pip install -r requirements.txt
"

echo "[7/10] File .env (SECRETS) se non esiste"
if [[ ! -f "${APP_DIR}/.env" ]]; then
  sudo tee "${APP_DIR}/.env" >/dev/null <<'ENVEOF'
# Binance
BINANCE_API_KEY=
BINANCE_API_SECRET=

# IBKR (IB Gateway locale)
IBKR_HOST=127.0.0.1
IBKR_PORT=4002
IBKR_CLIENT_ID=7

# Telegram alerts (opzionale)
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
ENVEOF
  sudo chown "${APP_USER}:${APP_USER}" "${APP_DIR}/.env"
  sudo chmod 600 "${APP_DIR}/.env"
  echo "Creato ${APP_DIR}/.env -> COMPILA le variabili (chmod 600)."
fi

echo "[8/10] Firewall (UFW) - solo SSH pubblico"
sudo ufw allow OpenSSH
# NON aprire porte IBKR (4001/4002) verso internet
sudo ufw --force enable

echo "[9/10] Systemd service"
SERVICE_PATH="/etc/systemd/system/autotrader.service"
sudo tee "${SERVICE_PATH}" >/dev/null <<EOF
[Unit]
Description=AutoTrader (Binance + IBKR)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${APP_USER}
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/.venv/bin/python -m app.main --mode paper --venue both
Restart=always
RestartSec=5
# hardening base
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true
ReadWritePaths=${APP_DIR}

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable autotrader.service

echo "[10/10] Avvio servizio"
sudo systemctl restart autotrader.service

echo "OK ✅"
echo "Comandi utili:"
echo "  sudo systemctl status autotrader.service"
echo "  journalctl -u autotrader.service -f"
echo "  sudo systemctl stop autotrader.service"
