#! C:\Users\mark\Developer\Python\wsjtx-udp\.venv\scripts\pythonw.exe
import socket
import struct
from threading import Thread
from tkinter import Event

from rx_msg import parse
from event import UPDATE_CALLS, UPDATE_STATUS
from wsjtx_db import wsjtx_db
from settings import settings
from tx_msg import heartbeat

WSJTX_PORT = 2237
HOST = '224.0.0.1'

# set to None (no capture) or filename
CAPTURE_DATA = None

class Receive:
    def __init__(self, gui):
        if CAPTURE_DATA is not None:
            self.data_out = open(CAPTURE_DATA, 'w')
        self.gui = gui
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1.0)
        self.thread = Thread(target=self.client)
        self.addr = None
        self.running = True
        host = HOST
        if int(HOST.split('.')[0]) in range(224,240):
            # multicast
            mreq = struct.pack("4sl", socket.inet_aton(HOST), socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            host = ''
        self.sock.bind((host, WSJTX_PORT))


    def send(self, data):
        if self.addr is not None:
            self.sock.sendto(data, self.addr)

    def start(self):
        self.thread.start()
        
    def stop(self):
        self.running = False
        self.thread.join()
        if CAPTURE_DATA is not None:
            self.data_out.close()

    def process_decodes(self, decodes):
        pota = []
        cq = []
        call = []
        for i in decodes:
            dx_call = None
            msg_parse = i.message.split(' ')
            if msg_parse[0] == 'CQ':
                if msg_parse[1] == 'POTA':
                    dx_call = msg_parse[2]
                    append = pota
                else:
                    dx_call = msg_parse[1]
                    append = cq
            elif msg_parse[0] == settings.de_call:
                dx_call = msg_parse[0]
                append = call
            else:
                # print(i.message, msg_parse)
                continue
            if dx_call is not None:    
                if settings.activator:
                    ex = wsjtx_db.exists_activator(dx_call, i)
                else:
                    ex = wsjtx_db.exists_hunter(dx_call, i)
                # print(ex)
                if ex[0] == 1:
                    continue
                append.append(i)                   
        pota.sort(key=lambda a: a.snr, reverse=True)
        call.sort(key=lambda a: a.snr, reverse=True)
        cq.sort(key=lambda a: a.snr, reverse=True)
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
                if CAPTURE_DATA is not None:
                    print(f'{data},', file=self.data_out)
                d = parse(data)
            except TimeoutError:
                continue
            msg_id = d.msg_id
            if settings.syncing:
                if msg_id == 2:
                    t = d.time
                    if old_time is None:
                        old_time = t
                    else:
                        if d != old_time:
                            settings.syncing = False
                            cycles = 0
                            r = [d]
                    continue
            match msg_id:
                case 0:  # HEARTBEAT
                    self.send(heartbeat())
                    # print('heartbeat sent')
                case 1:  # STATUS
                    Event.VirtualEventData = (d.tx_msg if d.transmitting else 'RX')
                    self.gui.event_generate(UPDATE_STATUS, when='tail')

                    settings.update_status(d)
                    if not d.decoding:
                        # print('done decoding')
                        cycles += 1
                        if cycles == 3 or settings.mode == 'FT4':
                            cycles = 0
                            self.process_decodes(r)
                            r = []
                case 2:  # DECODE 
                    r.append(d)
                case 5:  # LOG
                    wsjtx_db.add(d)
                case 12:  # ADIF
                    wsjtx_db.add_log(d.text)
                    


if __name__ == '__main__':
    from main import main
    main()

