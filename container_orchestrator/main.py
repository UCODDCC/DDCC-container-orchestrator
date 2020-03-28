from container_orchestrator.tcp.TcpServer import TcpServer

def setup():
    global server
    print("init!")
    server = TcpServer(7655)


def loop():
    global server
    print("loop!")
    server.handle_next_connection()



