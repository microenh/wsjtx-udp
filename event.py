from enum import Enum, auto
from queue import Queue, Empty
from threading import Lock

class NotifyGUI(Enum):
    QUIT = auto()
    CALLS = auto()
    STATUS = auto()
    GPGGA = auto()


class Manager:
    def  __init__(self):
        self.lock = Lock()
        self.running = True
        self.event_generate = lambda: None
        self.queue = Queue()

    def send(self, id_, data=None):
        if self.running:
            with self.lock:
                self.queue.put((id_, data))
                self.event_generate()

    def get_data(self):
        try:
            return self.queue.get_nowait()
        except Empty:
            return None
        
manager = Manager()
