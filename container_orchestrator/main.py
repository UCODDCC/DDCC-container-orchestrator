import signal, sys, time
from dotenv import load_dotenv
from pathlib import Path
from container_orchestrator.tcp.TcpServer import TcpServer
from container_orchestrator.orchestrator.Orchestrator import Orchestrator

def signal_handler(sig, frame):
    orchestrator.exit()
    time.sleep(3)
    sys.exit(0)

def setup():
    global orchestrator
    global server
    load_dotenv(dotenv_path=Path('.env'))
    signal.signal(signal.SIGINT, signal_handler)
    print("init!")
    orchestrator = Orchestrator(base_port=7000, top_port=7100)
    server = TcpServer(7655)

def loop():
    global orchestrator
    global server
    print("loop!")
    server.handle_next_connection(orchestrator)
