from enum import Enum, auto

EVENT = '<<EVENT>>'

class WSJTXEvent(Enum):

    QUIT = auto()
    TURN = auto()
    DU = auto()
    BUTTON = auto()
    FREQA = auto()
    STEP = auto()
