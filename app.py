#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
from container_orchestrator import main
from container_orchestrator.orchestrator.Orchestrator import Orchestrator
from container_orchestrator.config import *


if __name__ == '__main__':
    main.setup()
    while True:
        main.loop()
        time.sleep(1)
