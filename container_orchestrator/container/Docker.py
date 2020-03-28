import docker, time
from datetime import datetime
from container_orchestrator.tcp.TcpClient import TcpClient

def translateResourceName(resource):
    if resource == 'matrix':
        return "ucoddcdmatrix"

    raise Exception("translation could not be found")

class Docker:
    def __init__(self, resource, port):
        self.__resource = resource
        self.__port = port
        self.__client = docker.from_env()
        self.__running = False
        self.__is_operable = True
        self.__container = self.__client.containers.create(
            translateResourceName(self.__resource),
            hostname=self.__resource + ":" + str(self.__port),
            detach=True,
            ports={self.__port: str(self.__port)},
            environment={
                'PORT': self.__port,
                'RESOURCE': self.__resource,
                'HOSTNAME': str(self.__resource) + ":" + str(self.__port),
            },
        )
        self.__last_assignation = datetime.now()

    def start(self):
        if not self.isOperable():
            return False
        self.__container.start()
        self.__running = True
        return True

    def stop(self):
        if not self.isOperable():
            return False
        if not self.isAvailable():
            return False
        self.__running = False
        self.__container.reload()
        self.__container.stop(timeout=10)
        return True

    def remove(self):
        if not self.isAvailable():
            return False
        self.__is_operable = False
        self.__container.reload()
        self.__container.remove(force=True)
        return True

    def getPort(self):
        return self.__port

    def getResourceName(self):
        return self.__resource

    def getUsage(self):
        if not self.isOperable():
            return False
        return self.__container.top()

    def isAvailable(self):
        if not self.isOperable():
            return False
        return self.isRunning() and self.isIdle()

    def isRunning(self, timeout=10):
        if not self.__is_operable:
            return False
        if not self.isIdle():
            return True
        try:
            client = TcpClient("0.0.0.0", self.__port, timeout)
            client.send_message(B'+<up?>')
        except Exception as e:
            print(e)
            time.sleep(timeout)
            return False
        response = client.listen()
        if response == b'+<yes>':
            print("successful running response:", response)
            return True
        print("failure running response:", response)
        return False

    def isIdle(self):
        return True
        if not self.isOperable():
            return False
        result = self.__container.exec_run("cat /idle")
        if result[0] != 0:
            self.__is_operable = False
            return False
        return result[1] == b"0"

    def isOperable(self):
        return self.__is_operable

    def updateAssignationTime(self):
        self.__last_assignation = datetime.now()

    def getIdleTime(self):
        return datetime.now() - self.__last_assignation
