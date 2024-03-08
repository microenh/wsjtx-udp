import socket
from struct import pack
from threading import Thread
from manager import manager

class UDPClientBase:
    def __init__(self, address):
        self.address = address
        self.thread = Thread()
        self.do_close = False

    def close_socket(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.sock.close()
        self.report(False)

    def start(self):
        if not self.thread.is_alive():
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(2.0)
                self.sock.connect(self.address)
                self.thread = Thread(target=self.run)
                self.thread.start()
                self.report(True)
            except OSError:
                self.close_socket()
        
    def send(self, data):
        if not self.sock._closed:
            self.sock.sendall(data)

    def push(self, id_, data=None):
        manager.push(id_, data)

    def stop(self):
        if self.thread.is_alive():
            self.thread.join()
        
    def run(self):
        while manager.running:
            try:
                if self.do_close:
                    self.do_close = False
                    break
                self.process(self.sock.recv(2048))
            except OSError:
                break
            except TimeoutError:
                # print('timeout')
                continue
        self.close_socket()


if __name__ == '__main__':
    from main import Main
    Main()
