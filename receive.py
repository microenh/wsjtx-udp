import socket
import struct
from threading import Thread, Lock
from tkinter import Event

from rx_msg import parse
from event import NotifyGUI
from manager import manager
from wsjtx_db import wsjtx_db
from settings import settings
from tx_msg import heartbeat
from utility import timestamp

class Receive:
    def __init__(self):
        if settings.capture_data is not None:
            self.data_out = open(settings.capture_data, 'w')
        else:
            self.data_out = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1.0)
        self.thread = Thread(target=self.client)
        self.addr = None
        host = settings.host
        if int(host.split('.')[0]) in range(224,240):
            # multicast
##            mreq = struct.pack("4sl",
##                               socket.inet_aton(settings.host),
##                               socket.INADDR_ANY)
            mreq = struct.pack("4sii",
                               socket.inet_aton(host),
                               socket.INADDR_ANY, 0)
            self.sock.setsockopt(socket.IPPROTO_IP,
                                 socket.IP_ADD_MEMBERSHIP,
                                 mreq)
            host = ''
        self.sock.bind((host, settings.wsjt_port))


    def start(self):
        self.thread.start()

    def send(self, data):
        if self.addr is not None:
            self.sock.sendto(data, self.addr)

        
        
    def stop(self):
        self.thread.join()
        if self.data_out is not None:
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
        manager.push(NotifyGUI.WSJTX_CALLS, (pota, call, cq))
        
    def client(self):
        r = []
        while manager.running:
            try:
                data, self.addr = self.sock.recvfrom(1024)
                if self.data_out is not None:
                    print(f'{data},', file=self.data_out)
                d = parse(data)
            except TimeoutError:
                continue
            msg_id = d.msg_id
            match msg_id:
                case 0:  # HEARTBEAT
                    # print('heartbeat')
                    manager.push(NotifyGUI.WSJTX_HB)
                    self.send(heartbeat())
                case 1:  # STATUS
                    print(f'{timestamp()} decode: {d.decoding}')
                    # print('status')
                    settings.update_status(d)
                    manager.push(NotifyGUI.WSJTX_STATUS, d)
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

