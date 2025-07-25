#!/bin/bash

VENV_DIR=".venv"

# Schritt 1: Prüfen, ob venv existiert
if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Erstelle virtuelles Environment..."
    python3 -m venv $VENV_DIR
    source $VENV_DIR/bin/activate
    echo "[+] Installiere Abhängigkeiten..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source $VENV_DIR/bin/activate
fi

# Schritt 2: Starte dein Python-Programm
echo "[+] Starte ISS Tracker..."
python iss_tracker.py live 600
echo
read -p "Drücke Enter zum Beenden..."

