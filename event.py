from enum import Enum, auto
from queue import Queue, Empty
from threading import Lock

NOTIFY_GUI = '<<NOTIFY_GUI>>'
lock = Lock()

class NotifyGUI(Enum):
    QUIT = auto()
    CALLS = auto()
    STATUS = auto()
    GPGGA = auto()

notify_queue = Queue()

__all__ = ('NOTIFY_GUI', 'NotifyGUI', 'notify_queue', 'Empty', 'lock')
