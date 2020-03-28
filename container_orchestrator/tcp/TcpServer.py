import socket
import threading


def handle_client_connection(client_socket):
    request = client_socket.recv(2048)
    print('Received {}'.format(request))
    response = '+<5555>'
    client_socket.send(response.encode(encoding='utf-8', errors='strict'))
    client_socket.close()


class TcpServer:
    def __init__(self, port):
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind(('0.0.0.0', port))
        self.__server.listen(5)

    def handle_next_connection(self):
        client_sock, address = self.__server.accept()
        print('Accepted connection from {}:{}'.format(address[0], address[1]))
        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock,)
        )
        client_handler.start()
