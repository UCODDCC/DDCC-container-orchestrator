#!/usr/bin/python3
# -*- coding: utf-8 -*-
from dotenv import load_dotenv
from pathlib import Path
import time

load_dotenv(dotenv_path=Path('.env'))

from container_orchestrator import main

if __name__ == '__main__':
    main.setup()
    while True:
        main.loop()
        time.sleep(1)
