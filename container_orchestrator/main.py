import signal, sys, time, os
from container_orchestrator.tcp.TcpServer import TcpServer
from container_orchestrator.orchestrator.Orchestrator import Orchestrator

def signal_handler(sig, frame):
    orchestrator.exit()
    time.sleep(3)
    sys.exit(0)

def setup():
    global orchestrator
    global server
    signal.signal(signal.SIGINT, signal_handler)
    if str(os.getenv('DEBUG')) == "True":
        print("init!")
    orchestrator = Orchestrator(base_port=int(os.getenv('BASE_PORT')), top_port=int(os.getenv('TOP_PORT')))
    server = TcpServer(int(os.getenv('PORT')))

def loop():
    global orchestrator
    global server
    if str(os.getenv('DEBUG')) == "True":
        print("loop!")
    server.handle_next_connection(orchestrator)
