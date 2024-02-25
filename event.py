from enum import Enum, auto
from queue import Queue, Empty


NOTIFY_GUI = '<<NOTIFY_GUI>>'

class NotifyGUI(Enum):
    CALLS = auto()
    STATUS = auto()

notify_queue = Queue()

__all__ = ('NOTIFY_GUI', 'NotifyGUI', 'notify_queue', 'Empty')
