from enum import Enum, auto

class NotifyGUI(Enum):
    QUIT = auto()

    HB = auto()
    
    CALLS = auto()
    STATUS = auto()
    
    GPS_OPEN=auto()
    GPS_CLOSE=auto()
    GPS_MSG=auto()
    GPRMC=auto()

