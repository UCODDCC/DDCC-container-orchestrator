from datetime import datetime, timedelta
from container_orchestrator.container.Docker import Docker as Container


class Orchestrator:
    def __init__(self, base_port=7000, top_port=7999, max_queue=50):
        self.__containers = []
        self.__base_port = base_port
        self.__top_port = top_port

    def requestAvailableContainer(self, resource, timeout=10):
        print("finding container")
        for container in self.getAvailableContainers():
            if container.getResourceName() == resource:
                print("available container found")
                return container
        return self.createContainer(resource, timeout)

    def createContainer(self, resource, timeout=10):
        print("creating container")
        if self.getAvailablePort() is None:
            return None
        container = Container(resource, self.getAvailablePort())
        container.start()
        if not container.isRunning():
            print("no response")
            try:
                container.remove()
            except Exception as e:
                print(e)
            return None
        # TODO: critical section!
        self.__containers.append(container)
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
