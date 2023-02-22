import threading
import socket
import time
import json
from typing import Dict, List
from loguru import logger

from settings import HOST
from settings import PACKAGE_SIZE

logger.add("file.log", backtrace=True, diagnose=True) 

class ISynchronizedObject:
    instanceCounter = 0
    def __init__(self, *args, **kwargs):
        type(self).instanceCounter += 1

    @staticmethod
    def initSyncObject(cls, dict_):
        return cls(**cls.getInitSyncObjectData(dict_))

    @staticmethod
    def getInitSyncObjectData(packageDict):
        """Для переназначения: вернуть словарь для инициализации, исходя из пришедшего пакета"""

    def setPackageAttribute(self, client, packageAttribute=None):
        if not packageAttribute:
            self.packageAttribute = f"{type(self).__name__}-InId:{self.instanceCounter}-CId:{client.id}"
        else:
            self.packageAttribute = packageAttribute
        
    def getPackingData(self) -> Dict:
        """Вернуть данные для синхронизации в формате {"имя_класса имя_объекта": {...} }"""
        attrs = self.returnPackingData()
        return {self.packageAttribute: attrs}

    def setPackingData(self, dictionary):
        """Для переназначения"""

    def returnPackingData(self) -> Dict:
        """Для переназначения: return {"...": ... , ...}"""

    def remove(self):
        for _ in self.groups():
            _.remove(self)
        print(self.groups())


class GameTCPClient(threading.Thread):
    def __init__(self, host, syncObjectsClasses, globalsEnabled=False):
        """Передать или список классов, или globals() для автоотбора и флаг globalsEnabled"""
        super().__init__(target=self)
        self.isDaemon = True

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.client_socket.connect(host)

        self.syncObjectsClasses = {}
        if globalsEnabled:
            for k, v in syncObjectsClasses.items():
                if type(v) is not type:
                    continue
                if ISynchronizedObject in v.__bases__:
                    self.syncObjectsClasses[k] = v
        else:
            self.syncObjectsClasses = {clss.__name__: clss for clss in syncObjectsClasses}

        self.id = None
        
        self.syncObjects = {}
        self.data = []
        self.package = None

        self.isInitDone = threading.Event()

    def run(self):
        self.runPackageCycle()

    def runPackageCycle(self):
        self.id = self.recv(1).decode()
        self.syncObjects[self.id] = {}
        self.syncObjects["s"] = {}
        self.isInitDone.set()
        while True:
            if self.client_socket.fileno() == -1:
                break
            if not self.getPackage() and self.data:
                data = self.formJSON(self.data)
                # logger.debug(f"Send: {data}")
                self.send(data.encode())
                package = self.recv(PACKAGE_SIZE).decode()
                # logger.debug(f"Received: {package}")
                self.packageReceived(package)

    def processPackage(self, pack):
        pack = json.loads(pack) 
        for _ in pack.keys():
            if pack[_] == None:
                continue
            elif pack[_] == "closed":
                if _ in self.syncObjects:
                    otherObjects = self.syncObjects[_]  
                    for obj in otherObjects.values():
                        obj.remove()
                    self.syncObjects.pop(_)
                continue
            for obj in pack[_].keys():
                if obj in self.getSyncObjectsList():
                    if "-" in obj:
                        obj_id = obj.split("-")[2].split(":")[1]
                    else:
                        obj_id = "s"
                    self.syncObjects[obj_id][obj].setPackingData(pack[_][obj])
                elif obj not in self.getSyncObjectsList():
                    objData = pack[_][obj]
                    newObj = self.createSyncInstance(_, obj, objData)

    def recv(self, size):
        return self.client_socket.recv(size)
    
    def send(self, data):
        self.client_socket.sendall(data)

    def formJSON(self, data):
        completeDict = {}
        for _ in data:
            completeDict.update(_.getPackingData())
        return json.dumps(completeDict)

    def packageReceived(self, package):
        self.package = package

    def getPackage(self):
        return self.package

    def donePackage(self):
        self.package = None

    def getSyncObjectsList(self):
        syncObjectsList = []
        for _ in self.syncObjects.values():
            syncObjectsList += _
        return syncObjectsList

    def synchronize(self, syncObjectClass: ISynchronizedObject, packageAttribute, **kwargs):
        """Возвращает экземпляр класса. packageAttribute = None - автоматическое присвоение имени"""
        syncObj = syncObjectClass(**kwargs)
        if not packageAttribute:
            syncObj.setPackageAttribute(self)
            self.syncObjects[self.id][syncObj.packageAttribute] = syncObj
        else:
            syncObj.setPackageAttribute(self, packageAttribute)
            self.syncObjects["s"][syncObj.packageAttribute] = syncObj
        self.data.append(syncObj)
        return syncObj


    def createSyncInstance(self, id, packageAttribute, dict_):
        objClass = self.syncObjectsClasses[packageAttribute.split("-")[0]]
        newInst = objClass.initSyncObject(objClass, dict_)
        if id not in self.syncObjects:
            self.syncObjects[id] = {}
        self.syncObjects[id][packageAttribute] = newInst
        return newInst


    def close(self):
        self.client_socket.close()