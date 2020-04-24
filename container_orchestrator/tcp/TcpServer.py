import socket, threading, os, sys


def handle_client_connection(client_socket, orchestraror):
    request = client_socket.recv(2048)
    if str(os.getenv('DEBUG')) == "True":
        sys.stderr.write('Received {}\n'.format(request))
    opcode = request.decode('utf-8').split('<')[1].split('>')[0]
    container = orchestraror.requestAvailableContainer(resource=opcode)
    if container is None:
        container = orchestraror.createContainer(resource=opcode)
    if container is None:
        client_socket.send("-server overload<no resource is available>".encode(encoding='utf-8', errors='strict'))
        return
    client_socket.send(("+<" + str(os.getenv('DOMAIN')) + ":" + str(container.getPort()) + ">").encode(encoding='utf-8', errors='strict'))
    client_socket.close()

class TcpServer:
    def __init__(self, port):
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind(('0.0.0.0', port))
        self.__server.listen(5)

    def handle_next_connection(self, orchestrator):
        client_sock, address = self.__server.accept()
        if str(os.getenv('DEBUG')) == "True":
            sys.stderr.write('Accepted connection from {}:{}\n'.format(address[0], address[1]))
        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock,orchestrator,)
        )
        client_handler.start()

    def exit(self):
        self.__server.close()