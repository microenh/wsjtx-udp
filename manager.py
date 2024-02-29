from queue import Queue, Empty
from threading import Lock

class Manager:
    def  __init__(self):
        self.lock = Lock()
        self.running = True
        self.event_generate = lambda: None
        self.queue = Queue()

    def push(self, id_, data=None):
        if self.running:
            with self.lock:
                self.queue.put((id_, data))
                self.event_generate()

    def pop(self):
        if self.running:
            try:
                return self.queue.get_nowait()
            except Empty:
                pass
        
manager = Manager()
