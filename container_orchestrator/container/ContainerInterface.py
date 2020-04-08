from datetime import datetime

class ContainerInterface:
    def __init__(self, resource, port):
        self.__resource = resource
        self.__port = port
        self.__is_operable = True
        self.__last_assignation = datetime.now()

    def start(self):
        pass

    def stop(self):
        pass

    def remove(self):
        pass

    def getPort(self):
        return self.__port

    def getResourceName(self):
        return self.__resource

    def getUsage(self):
        return 0

    def isAvailable(self):
        return self.isRunning() and self.isIdle()

    def isRunning(self):
        return False

    def isIdle(self):
        return True

    def isOperable(self):
        return self.__is_operable

    def markAsToRemove(self):
        self.__is_operable = False

    def updateAssignationTime(self):
        self.__last_assignation = datetime.now()

    def getIdleTime(self):
        return datetime.now() - self.__last_assignation
