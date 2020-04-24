import signal, sys, time, os, threading
from container_orchestrator.tcp.TcpServer import TcpServer
from container_orchestrator.orchestrator.Orchestrator import Orchestrator

def signal_handler(sig, frame):
    orchestrator.exit()
    time.sleep(3)
    sys.exit(0)

def garbageCollector():
    global orchestrator
    while True:
        time.sleep(5)
        orchestrator.garbageCollector()

def setup():
    global orchestrator
    global server
    signal.signal(signal.SIGINT, signal_handler)
    if str(os.getenv('DEBUG')) == "True":
        sys.stderr.write("init!\n")
    orchestrator = Orchestrator(base_port=int(os.getenv('BASE_PORT')), top_port=int(os.getenv('TOP_PORT')))
    server = TcpServer(int(os.getenv('PORT')))
    garbage_collector_thread = threading.Thread(target=garbageCollector)
    garbage_collector_thread.start()

def loop():
    global orchestrator
    global server
    #if str(os.getenv('DEBUG')) == "True":
    #    sys.stderr.write("loop!\n")
    server.handle_next_connection(orchestrator)
