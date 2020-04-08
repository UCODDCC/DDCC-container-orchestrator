import docker, time, os
from datetime import datetime, timedelta
from container_orchestrator.tcp.TcpClient import TcpClient


def translateResourceName(resource):
    if resource == 'matrix':
        return "ucoddccmatrix"
    elif resource == 'vector':
        return "ucoddccvector"

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
                'PORT': str(self.__port),
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
        return self.isRunning() and self.isIdle()

    def isRunning(self):
        if not self.__is_operable:
            return False
        try:
            result = self.__container.exec_run("cat /idle")
        except Exception as e:
            print(e)
            return False
        if str(os.getenv('DEBUG')) == "True":
            print("running cat:", result)
        if result[0] == 0:
            return True
        return False

    def isIdle(self):
        if not self.isOperable():
            return False
        if not self.isRunning():
            return False
        result = self.__container.exec_run("cat /idle")
        if str(os.getenv('DEBUG')) == "True":
            print("idling cat:", result)
        if result[0] != 0:
            self.__is_operable = False
            return False
        if str(os.getenv('DEBUG')) == "True":
            print("cat /idle->", result[1])
        if result[1] == b'1':
            ttl = timedelta(seconds=int(os.getenv('MINIMUM_IDLETIME_TO_BE_AVAILABLE')))
            return ttl < self.getIdleTime()
        return False

    def isOperable(self):
        return self.__is_operable

    def updateAssignationTime(self):
        self.__last_assignation = datetime.now()

    def getIdleTime(self):
        return datetime.now() - self.__last_assignation
