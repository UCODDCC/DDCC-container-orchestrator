import socket
import threading
from container_orchestrator.tcp.TcpClient import TcpClient
from container_orchestrator.orchestrator.Orchestrator import Orchestrator

def handle_client_connection(client_socket, orchestraror):
    request = client_socket.recv(2048)
    opcode="matrix"
    print('Received {}'.format(request))
    port = orchestraror.requestAvailableContainer(resource=opcode).getPort()
    if port is None:
        port = orchestraror.createContainer(resource=opcode).getPort()
    if port is None:
        client_socket.send("-server overload<no resource is available>".encode(encoding='utf-8', errors='strict'))
        return
    client = TcpClient(ip='127.0.0.1', port=port)
    print('to docker {}'.format(request))
    client.send_message(request)
    response = client.listen()
    print('from docker {}'.format(response))
    client_socket.send(response)
    client_socket.close()



class TcpServer:
    def __init__(self, port):
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind(('0.0.0.0', port))
        self.__server.listen(5)

    def handle_next_connection(self, orchestrator):
        client_sock, address = self.__server.accept()
        print('Accepted connection from {}:{}'.format(address[0], address[1]))
        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock,orchestrator,)
        )
        client_handler.start()

    def exit(self):
        self.__server.close()