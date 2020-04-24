from datetime import timedelta
import time, threading, os, sys
from container_orchestrator.container.Docker import Docker as Container



class Orchestrator:
    def __init__(self, base_port=7000, top_port=7999, max_queue=50):
        self.__containers = []
        self.__base_port = base_port
        self.__top_port = top_port
        self.__lock = threading.Lock()


    def garbageCollector(self):
        #if str(os.getenv('DEBUG')) == "True":
        #    sys.stderr.write("garbage collector loop\n")
        for container in self.__containers:
            if container.getIdleTime() > timedelta(seconds=int(os.getenv('MAX_IDLE_TIME_ALIVE'))):
                if container.isOperable():
                    if str(os.getenv('DEBUG')) == "True":
                        sys.stderr.write("garbage collector: marking container {} at port {} to be deleted\n".format(container.getResourceName(), container.getPort()))
                    container.markAsToRemove()
                    container.updateAssignationTime()
                    if str(os.getenv('DEBUG')) == "True":
                        sys.stderr.write("garbage collector: removing container {} at port {}\n".format(container.getResourceName(),container.getPort()))
                        sys.stderr.write("remove ret: {}\n".format(container.remove()))
                    self.__containers.remove(container)
                else:
                    if container.getIdleTime() > timedelta(seconds=int(os.getenv('TIME_FROM_MARK_AS_DELETE_TO_REMOVE'))):
                        if str(os.getenv('DEBUG')) == "True":
                            sys.stderr.write("garbage collector: removing container {} at port {}\n".format(container.getResourceName(), container.getPort()))
                            sys.stderr.write("remove ret: {}\n".format(container.remove()))
                        self.__containers.remove(container)

    def requestAvailableContainer(self, resource, timeout=10):
        sys.stderr.write("finding container\n")
        self.__lock.acquire(True)
        for container in self.getAvailableContainers():
            if container.getResourceName() == resource:
                if str(os.getenv('DEBUG')) == "True":
                    sys.stderr.write("available container found\n")
                container.updateAssignationTime()
                self.__lock.release()
                return container
        self.__lock.release()
        return None


    def createContainer(self, resource, timeout=10):
        if str(os.getenv('DEBUG')) == "True":
            sys.stderr.write("creating {} container\n".format(resource))
        self.__lock.acquire(True)
        if self.getAvailablePort() is None:
            self.__lock.release()
            return None
        port = self.getAvailablePort()
        if port is None:
            self.__lock.release()
            return None
        if str(os.getenv('DEBUG')) == "True":
            sys.stderr.write("creating container at, {}\n".format(port))
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
                sys.stderr.write("no response from container\n")
            try:
                container.remove()
            except Exception as e:
                print(e)
            self.__lock.release()
            return None
        container.updateAssignationTime()
        self.__containers.append(container)
        self.__lock.release()
        # TODO container can collide with other job while waiting for regional master to send work
        # TODO solution is to implement a x second timer in getavailresources with setnewop timer actualizer

        if str(os.getenv('DEBUG')) == "True":
            sys.stderr.write("newly created container\n")
        return container

    def getAvailablePort(self):
        used_ports = []
        for container in self.__containers:
            used_ports.append(container.getPort())
        for port in range(self.__base_port, self.__top_port + 1):
            if port not in used_ports:
                return port
        return None

    def getAvailableContainers(self):
        idle_containers = []
        for container in self.__containers:
            if container.isIdle():
                idle_containers.append(container)
        return idle_containers

    def removeContainerThreaded(self, container):
        container.remove()
        self.__containers.remove(container)

    def removeContainer(self, port):
        for container in self.__containers:
            if container.getPort() == port:
                container.stop()
                thread = threading.Thread(
                    target=self.removeContainerThreaded,
                    args=(self, container,)
                )
                thread.start()
                return True
        return False

    def exit(self):
        for container in self.__containers:
            container.stop()
            thread = threading.Thread(
                target=self.removeContainerThreaded,
                args=(self, container,)
            )
            thread.start()
