#! C:\Users\mark\Developer\Python\wsjtx-udp\.venv\scripts\pythonw.exe
import socket
import struct
from threading import Thread, Lock
from tkinter import Event

from rx_msg import parse
from event import *
from wsjtx_db import wsjtx_db
from settings import settings
from tx_msg import heartbeat

class Receive:
    def __init__(self, gui):
        if settings.CAPTURE_DATA is not None:
            self.data_out = open(settings.CAPTURE_DATA, 'w')
        self.gui = gui
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1.0)
        self.thread = Thread(target=self.client)
        self.addr = None
        self.running = True
        host = settings.HOST
        if int(settings.HOST.split('.')[0]) in range(224,240):
            # multicast
            mreq = struct.pack("4sl", socket.inet_aton(settings.HOST), socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            host = ''
        self.sock.bind((host, settings.WSJTX_PORT))


    def send(self, data):
        if self.addr is not None:
            self.sock.sendto(data, self.addr)

    def start(self):
        self.thread.start()
        
    def stop(self):
        self.thread.join()
        if settings.CAPTURE_DATA is not None:
            self.data_out.close()

    def notify_gui(self, id_, data):
        if settings.running:
            with lock:
                notify_queue.put((id_, data))
                self.gui.event_generate(NOTIFY_GUI, when='tail')
        

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
        self.notify_gui(NotifyGUI.CALLS, (pota, call, cq))
        
    def client(self):
        r = []
        while settings.running:
            try:
                data, self.addr = self.sock.recvfrom(1024)
                if settings.CAPTURE_DATA is not None:
                    print(f'{data},', file=self.data_out)
                d = parse(data)
            except TimeoutError:
                continue
            msg_id = d.msg_id
            match msg_id:
                case 0:  # HEARTBEAT
                    self.send(heartbeat())
                    # print('heartbeat sent')
                case 1:  # STATUS
                    settings.update_status(d)
                    self.notify_gui(NotifyGUI.STATUS, d)
                    if not d.decoding:
                        # print('done decoding')
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

