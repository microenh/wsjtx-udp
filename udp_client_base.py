import socket
from struct import pack
from threading import Thread
from manager import manager

class UDPClientBase:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1.0)
        self.sock.connect((host, port))
        self.thread = Thread(target=self.run)

    def start(self):
        self.thread.start()

    def send(self, data):
        self.sock.sendall(data)

    def push(self, id_, data=None):
        manager.push(id_, data)

    def stop(self):
        self.thread.join()
        
    def run(self):
        self.report_open()
        while manager.running:
            try:
                data = self.sock.recv(2048)
                # print(data)
                # print()
                self.process(data)
            except TimeoutError:
                # print('timeout')
                continue
        self.report_close()

