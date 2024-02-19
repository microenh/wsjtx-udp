#! C:\Users\mark\Developer\Python\wsjtx-udp\.venv\scripts\pythonw.exe
import socket
import struct
from threading import Thread
from tkinter import Event
from gui import Gui

from rx_msg import parse
##from tx_msg import (heartbeat, clear, reply, close, replay, halt_tx,free_text,
##    location, highlight_call)

WSJTX_PORT = 2237
HOST = '224.0.0.1'


IS_ALL_GROUPS = int(HOST.split('.')[0]) in range(224,240)

running = True
app = None

def process_decodes(decodes, de_call):
    pota = []
    cq = []
    call = []
    for i in decodes:
        msg = i['message']
        if 'POTA' in msg:
            pota.append(i)
        elif msg.startswith('CQ'):
            cq.append(i)
        elif msg.startswith(de_call):
            call.append(i)
    pota.sort(key=lambda a: a['snr'], reverse=True)
    call.sort(key=lambda a: a['snr'], reverse=True)
    cq.sort(key=lambda a: a['snr'], reverse=True)
    Event.VirtualEventData = pota + call + cq
    app.event_generate('<<UPDATE_CALLS>>', when='tail')

##    for i in r:
##        print(f"{i['snr']:3} {i['message']}")
##    print()
    

def client(sock):
    old_time = None
    r = []
    syncing = True
    cycles = 0
    ct = 0
    while running:
        d = parse(sock.recv(1024))
        msg_id = d['msg_id']
        if syncing:
            if msg_id == 2:
                t = d['time']
                if old_time is None:
                    old_time = t
                else:
                    if d != old_time:
                        syncing = False
                        cycles = 0
                        r = [d]
                continue
        match msg_id:
            case 1:
                if not d['decoding']:
                    cycles += 1
                    if cycles == 3:
                        cycles = 0
                        process_decodes(r, d['de_call'])
                        r = []
            case 2:
                r.append(d)

def setup_receive_thread(sock):
     #, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if IS_ALL_GROUPS:
        # on this port, receives ALL multicast groups
        sock.bind(('', WSJTX_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(HOST), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    else:
        # on this port, listen ONLY to host
        sock.bind((HOST, WSJTX_PORT))
    return Thread(target=client, args=(sock,))

def main():
    global app, running
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_thread = setup_receive_thread(sock)
    recv_thread.start()
    app = Gui()
    app.run()
    running = False
    recv_thread.join()

        
if __name__ == '__main__':
    main()
 

