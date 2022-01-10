import enum

class CrRadioState(enum.Enum):
    Init = 0
    Idle = 1
    AwaitingForImage = 2
    ImageSending = 4
    ImageRecieving = 8
    AwaitingCommand = 16
    Error = 7

class CrRadioEventResult(enum.Enum):
    Ok = 0
    GenericError = 1
    TimeoutError = 3
    NoInfoError = 13
    TypeError = 21


    def __bool__(self):
        if self.value == CrRadioEventResult.Ok.value:
            return True
        else:
            return False
    def __str__(self):
        return self.name
        
class CrRadioMessageType(enum.Enum):
    Command = 1
    ImagePiece = 3
    Ack = 9


class CrRadioCommand(enum.Enum):
    StartImage = 3
    FinishImage = 5

class WrongPackageSize(Exception):
    pass

class WrongPackageType(Exception):
    pass
