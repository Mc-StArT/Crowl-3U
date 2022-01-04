import RPi.GPIO as GPIO 
import time     
import spidev
from lib_nrf24 import NRF24
from RadioEnvironment import *
from time import sleep
GPIO.setmode(GPIO.BCM)


class CrRadio:

    PKG_OK = 12
    PKG_WRONG_SUM = 17
    PKG_ERROR = 13


    pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]
    def __init__(self,*, placement = 1, debug = False) -> None:
        self.state = CrRadioState.Init
        self.debug = debug
        self.radio = NRF24(GPIO,spidev.SpiDev())
        self.radio.begin(0, 5)
        time.sleep(1) 

        self.radio.setRetries(15,15)
        self.radio.setPayloadSize(32)
        self.radio.setChannel(0x60)

        self.radio.setDataRate(NRF24.BR_1MBPS)
        self.radio.setPALevel(NRF24.PA_MIN)

        self.radio.setAutoAck(True)
        self.radio.enableDynamicPayloads()
        self.radio.enableAckPayload()
        if placement == 1:
                
            self.radio.openWritingPipe(self.pipes[1])
            self.radio.openReadingPipe(1, self.pipes[0])
        else:
            self.radio.openWritingPipe(self.pipes[0])
            self.radio.openReadingPipe(1, self.pipes[1])
        self.state = CrRadioState.Idle
        # self.radio.printDetails()
    

    def getAck(self, *, desired = None):                                #! TODO: #1 Finish getAck function @TeaCupMe  
        _sentTime = time.time()
        buf = []
        while time.time()-_sentTime < 1 and not self.radio.available():
            pass
        if not self.radio.available():
            return CrRadioEventResult.TimeoutError
        self.radio.read(buf)
        if len(desired)!=len(buf):
            return CrRadioEventResult.GenericError
        elif desired and any(buf[i] != desired[i] for i in range(len(desired))):
            return CrRadioEventResult.GenericError
        else:
            return CrRadioEventResult.Ok

    def _sendCommand(self, command:int) -> CrRadioEventResult:
                                                                        
        buf = [0]*32                                                    #! TODO: #2 Write _sendCommand function @TeaCupMe
        buf[0] = command
        self.radio.write(buf)
        response = self.getAck()
        pass  

    def sendFile(self, filePath: str, ) -> CrRadioEventResult:          #! TODO: #3 Rewrite sendFile function as open API. @TeaCupMe
        self.state = CrRadioState.ImageSending

        if filePath.split(".")[-1]!="b64":
            raise TypeError(f"Wrong file type: .b64 expected, {filePath.split('.')[-1]} got")
        with open(filePath, "r") as file:
            data = file.read()
            # file.close()
        packedData = self._splitStringToPieces(data)
        print(f"Bytes to be transmitted: {len(data)}\nPackages to be transmitted: {len(packedData)}\nEstimated time: {self._estimateTime(packedData)}")
        
        self.radio.write(list("start"))
        for index in range(len(packedData)):
            _toSend = []
            # _toSend.append(index//65536)
            # _toSend.append((index%65536)//256)
            # _toSend.append(index%256)
            _toSend.extend(packedData[index])
            self.radio.write(_toSend)
            if self.radio.isAckPayloadAvailable():
                pl = []
                self.radio.read(pl, self.radio.getDynamicPayloadSize())
                print(f"Recieved ack with {pl}")
            else:
                print("Recieved only ack")
        self.radio.write(list("end"))
        
        return 0
    
    
    
    def recieveFile(self, fileName:str) -> int: #! TODO Rewrite
        if fileName.split(".")[-1]!="b64":
            raise TypeError("Unappropriate file format: expected .b64")
        with open(fileName, "w") as file:
            self.radio.startListening()
            buff = []
            string = ""
            i=1
            while not self.radio.available():
                self._print("Listening for file...")
            while not string[:5]=="start":
                while not self.radio.available([0]):
                    time.sleep(10000/1000000.0)
                self.radio.read(buff, 32)
                string == "".join([str(i) for i in buff])
                self.radio.writeAckPayload(1, [0, 1], len([0, 1]))
            buff=[]
            while not string[:3]=="end":
                buff=[]
                while not self.radio.available([0]):
                    time.sleep(10000/1000000.0)
                self.radio.read(buff, 32)
                string == "".join([str(i) for i in buff])
                self.radio.writeAckPayload(1, [0, 1], len([0, 1]))
                file.write("".join(buff))
            file.close()
            return 0

    def _hash(self, data:list):
        toBeHashed = data.copy()
        for i in range(len(toBeHashed)):
            if not isinstance(toBeHashed[i], int):
                toBeHashed[i] = str(toBeHashed[i]).encode(encoding="UTF-8")
        hsh = sum(toBeHashed)%255
        return hsh

    def _splitStringToPieces(self, string:str,*,  n=29) -> str:
        chunks = [string[i:i+n] for i in range(0, len(string), n)]
        chunks[-1] = chunks[-1]+"="*(n-len(chunks[-1]))
        return chunks, len(chunks)

    def _estimateTime(self, dt:list) -> int:
        
        _time = len(dt)/1000
        self._print(f"Estimated time: {_time}")
        return _time                #!!! TODO: Placeholder, requires replacement
    
    """def hasData(self) -> bool:      #*? Not needed
        data = []
        self.radio.read(data, 32)
        if len(data) != 32:
            return False
        if data.count(0)+data.count("0")>=30:
            return False
    """
        
    def _sendPackage(self, package) -> CrRadioEventResult:
        
        if not isinstance(package, (list)):
            self.state = CrRadioState.Error
            raise WrongPackageType(f"Package must be of type 'list', {type(package)} recieved")
            
        if not len(package) == 31:
            self.state = CrRadioState.Error
            raise WrongPackageSize(f"Package array must be of lenght 31, {len(package)} recieved")
        # if not all(0<=)                           #! TODO Content check required
        package.append(self._hash(package))
        self.radio.write(package)

    def _print(self, message):
        if self.debug:
            print(message)
        return
        
    def _parsePackage(self, package:list):          #! TODO: Finish parsing function
        self._print("Parsing package: "+"["+" ,".join(package))
        command = package[0]
