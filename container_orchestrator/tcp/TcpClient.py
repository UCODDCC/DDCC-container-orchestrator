import socket, select, os, sys


class TcpClient():
    def __init__(self, ip, port, timeout=10):
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client.connect((ip, port))
        self.__client.settimeout(timeout)

    def handle_client_connection(self, client_socket):
        request = client_socket.recv(1024)
        if str(os.getenv('DEBUG')) == "True":
            sys.stderr.write('Received {}\n'.format(request))
        client_socket.send("+<response here>")
        client_socket.close()

    def send_message(self, payload):
        self.__client.send(payload)

    def listen(self):
        response = self.__client.recv(2048)
        return response

    def exit(self):
        self.__client.close()
