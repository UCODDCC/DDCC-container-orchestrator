from datetime import datetime, timedelta
import time, threading, os
from container_orchestrator.container.Docker import Docker as Container



class Orchestrator:
    def __init__(self, base_port=7000, top_port=7999, max_queue=50):
        self.__containers = []
        self.__base_port = base_port
        self.__top_port = top_port
        self.__lock = threading.Lock()

    def requestAvailableContainer(self, resource, timeout=10):
        print("finding container")
        self.__lock.acquire(True)
        for container in self.getAvailableContainers():
            if container.getResourceName() == resource:
                if str(os.getenv('DEBUG')) == "True":
                    print("available container found")
                self.__lock.release()
                return container # TODO container can collide with other job while waiting for regional master to send work
                # TODO solution is to implement a x second timer in getavailresources with setnewop timer actualizer
        self.__lock.release()
        container = self.createContainer(resource, timeout)
        return container


    def createContainer(self, resource, timeout=10):
        if str(os.getenv('DEBUG')) == "True":
            print("creating container")
        self.__lock.acquire(True)
        if self.getAvailablePort() is None:
            self.__lock.release()
            return None
        port = self.getAvailablePort()
        if port is None:
            self.__lock.release()
            return None
        if str(os.getenv('DEBUG')) == "True":
            print("creating container at,", port)
        container = Container(resource, port)
        container.start()
        running = False
        while timeout > 0:
            if container.isRunning():
                running = True
                break
            time.sleep(1)
            timeout -= 1
        if not running:
            if str(os.getenv('DEBUG')) == "True":
                print("no response from container")
            try:
                container.remove()
            except Exception as e:
                print(e)
            self.__lock.release()
            return None
        self.__containers.append(container)
        self.__lock.release()
        # TODO container can collide with other job while waiting for regional master to send work
        # TODO solution is to implement a x second timer in getavailresources with setnewop timer actualizer

        if str(os.getenv('DEBUG')) == "True":
            print("newly created container")
        return container

    def getAvailablePort(self):
        used_ports = []
        for container in self.__containers:
            used_ports.append(container.getPort())
        for port in range(self.__base_port, self.__top_port):
            if port not in used_ports:
                return port
        return None

    def getAvailableContainers(self):
        idle_containers = []
        for container in self.__containers:
            if container.isAvailable():
                idle_containers.append(container)
        return idle_containers

    def removeContainer(self, port):
        for container in self.__containers:
            if container.getPort() == port:
                container.remove()
                return True
        return None

    def exit(self):
        for container in self.__containers:
            container.stop()
            container.remove()

'''
    def queuedWaitForResource(self, resource, timeout=10, ttl=datetime.now() + timedelta(seconds=60)):
        if self.__max_queue >= len(self.__resource_queue):
            return False
        self.__resource_queue.append((resource, timeout, ttl))
        return True

    def existsQueuedRequests(self):
        return not len(self.__resource_queue) == 0

    def resolveResourceQueue(self):
        for request in self.__resource_queue:
            if request[2] < datetime.now():
                self.__resource_queue.remove(request)

        for request in self.__resource_queue:
            container = self.requestAvailableContainer(request[0], request[1])
'''
