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


class CrRadioSendResult(CrRadioEventResult):
    a = 2


class WrongPackageSize(Exception):
    pass

class WrongPackageType(Exception):
    pass
