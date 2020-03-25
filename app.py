#!/usr/bin/python3
# -*- coding: utf-8 -*-

from dotenv import load_dotenv
from pathlib import Path
import signal, sys, time
from container_orchestrator import main

def signal_handler(sig, frame):
    time.sleep(3)
    sys.exit(0)

load_dotenv(dotenv_path=Path('.env'))

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        try:
            main.loop()
        except Exception as e:
            print(e)
        time.sleep(1)

