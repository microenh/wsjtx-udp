#! C:\Users\mark\Developer\Python\wsjtx-udp\.venv\scripts\pythonw.exe
import socket
import struct
from threading import Thread
from tkinter import Event

from rx_msg import parse
from event import UPDATE_CALLS

WSJTX_PORT = 2237
HOST = '224.0.0.1'

class Receive:
    def __init__(self, gui):
        self.gui = gui
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1.0)
        self.thread = Thread(target=self.client)
        self.running = True
        self.syncing = True
        host = HOST
        if int(HOST.split('.')[0]) in range(224,240):
            # multicast
            mreq = struct.pack("4sl", socket.inet_aton(HOST), socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            host = ''
        self.sock.bind((host, WSJTX_PORT))

    def send(self, data):
        self.sock.sendto(data, self.addr)

    def start(self):
        self.thread.start()
        
    def stop(self):
        self.running = False
        self.thread.join()

    def resync(self):
        self.syncing = True

    def process_decodes(self, decodes, de_call):
        pota = []
        cq = []
        call = []
        for i in decodes:
            msg = i['message']
            if msg.startswith('CQ POTA'):
                pota.append(i)
            elif msg.startswith('CQ'):
                cq.append(i)
            elif msg.startswith(de_call):
                call.append(i)
        pota.sort(key=lambda a: a['snr'], reverse=True)
        call.sort(key=lambda a: a['snr'], reverse=True)
        cq.sort(key=lambda a: a['snr'], reverse=True)
        Event.VirtualEventData = pota + call + cq
        self.gui.event_generate(UPDATE_CALLS, when='tail')
        
    def client(self):
        old_time = None
        r = []
        cycles = 0
        ct = 0
        while self.running:
            try:
                data, self.addr = self.sock.recvfrom(1024)
                d = parse(data)
            except TimeoutError:
                continue
            msg_id = d['msg_id']
            if self.syncing:
                if msg_id == 2:
                    t = d['time']
                    if old_time is None:
                        old_time = t
                    else:
                        if d != old_time:
                            self.syncing = False
                            cycles = 0
                            r = [d]
                    continue
            match msg_id:
                case 1:
                    if not d['decoding']:
                        cycles += 1
                        if cycles == 3:
                            cycles = 0
                            self.process_decodes(r, d['de_call'])
                            r = []
                case 2:
                    r.append(d)


if __name__ == '__main__':
    from main import main
    main()

