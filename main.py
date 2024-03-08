import os
import tkinter as tk
from tkinter import scrolledtext, ttk
from settings import settings

from isdark import isDark
from PIL import Image, ImageTk
from tx_msg import reply, free_text, halt_tx, clear

from event import NotifyGUI
from manager import manager
from utility import timestamp
from datetime import datetime, timezone

from wsjtx import WSJTX

if settings.platform == 'win32':
    from gps import GPS
else:
    from gps_udp import GPS



class Main(tk.Tk):
    """Main class more"""
    LOGO = os.path.join(os.path.dirname(__file__), "Logo.png")

    def __init__(self):
        super().__init__()
        self.screenName = ':0.0'
        if os.environ.get('DISPLAY', '') == '':
            os.environ.__setitem__('DISPLAY', ':0.0')
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.bind(n := '<<GUI>>', self.do_notify)
        manager.event_generate = lambda: self.event_generate(n, when="tail")

        # self.after_idle(lambda: self.eval('tk::PlaceWindow . center'))
        self.last_decode = None
        self.setup_variables()
        self.setup_theme()
        self.layout()
        self.grid = None
        self.has_gps = False
        self.after_task = None
        self.start()

    def setup_variables(self):
        self.rx_tx = tk.StringVar()
        self.gps_text = tk.StringVar()
        self.update_rx_tx(False)
        self.gps_button = tk.StringVar()
        self.time_button = tk.StringVar()
        self.park = tk.StringVar()
    
    def setup_theme(self):
        self.style = ttk.Style(self)
        self.last_dark = None
        # Import the tcl files
        self.tk.call('source', 'forest-dark.tcl')
        self.tk.call('source', 'forest-light.tcl')
        # Set the theme with the theme to match the system theme
        self.after_task = self.check_dark()

    def layout(self):
        self.resizable(False, False)
        self.title('POTA-FT8/FT4 Helper')
        self.image = ImageTk.PhotoImage(Image.open(self.LOGO))
        self.iconphoto(False, self.image)
        
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='y')
        ttk.Label(main_frame, image=self.image).pack()
        
        bg = ttk.Frame(main_frame)
        bg.pack(padx=10)

        f = ttk.Frame(bg)
        f.pack(pady=(0,10))
        tx_rx = ttk.Label(f, textvariable=self.rx_tx)
        tx_rx.pack(anchor='center')
        tx_rx.bind('<Double-1>', self.abort_tx)

        cb = ttk.Frame(bg)
        cb.pack(expand=True, fill='y', pady=(0,10))
        
        self.calls_pota = self.callentrybox(cb)
        self.calls_me = self.callentrybox(cb)
        self.calls_cq = self.callentrybox(cb)

        self.lookup = {self.calls_pota: {}, self.calls_me: {}, self.calls_cq: {}}
        self.call_data = {self.calls_pota: [], self.calls_me: [], self.calls_cq: []}

        f = ttk.Frame(bg)
        f.pack(fill='x', pady=10)
        ttk.Label(f, text="Park").pack(side='left')
        ttk.Entry(f, textvariable=self.park).pack(fill='x', padx=(10,0))

        f = ttk.Frame(bg)
        f.pack(fill='x', pady=(0,10))
        ttk.Label(f, text='GPS').pack(side='left')
        ttk.Label(f, textvariable=self.gps_text).pack(side='left', fill='x', padx=(10,0))
        
        self.socket_button = ttk.Button(f, text='SOCKET', command=self.do_socket_button)
        self.socket_button.pack(side='right')
        
        self.time_button = ttk.Button(f, command=self.do_time_button)
        self.time_button.pack(side='right', padx=(0,10))
        
        self.grid_button = ttk.Button(f, command=self.do_grid_button)
        self.grid_button.pack(side='right', padx=(0,10))
        
        self.geometry('+1940+40')

    def do_grid_button(self):
        if not self.has_gps:
            self.gps.start()
        else:
            self.gps.update_grid(self.grid, self.wsjtx)
            
    def do_time_button(self):
        self.gps.update_time()

    def do_socket_button(self):
        self.gps.do_close = True


    def abort_tx(self, _):
        self.receive.send(halt_tx(True))        
        self.receive.send(halt_tx(False))        

    def callentrybox(self, frame):
        f = ttk.Frame(frame)
        f.pack(side='left', expand=True, fill='y')
        c = ttk.Treeview(f, height=10, show='tree')
        c.pack(side='left')
        vsb = ttk.Scrollbar(f, orient="vertical", command=c.yview)
        vsb.pack(expand=True, fill='y')
        
        c.configure(yscrollcommand=vsb.set)

        c['columns'] = ('SNR','Message')
        c.column('#0', width=0, stretch='no')
        c.column('SNR', width=30, stretch='no')
        c.column('Message', width=150, stretch='yes')

        c.bind('<Double-1>', lambda e: self.do_call(e, c))
        c.bind('<Return>', lambda e: self.do_call(e, c))

        return c

        

    def do_notify(self, _):
        while True:
            data = manager.pop()
            if data is None:
                break
            id_, d = data
            # print('ID', id_)
            match id_:
                case NotifyGUI.QUIT:
                    self.quit()
                case NotifyGUI.WSJTX_HB:
                    pass
                case NotifyGUI.WSJTX_CALLS:
                    self.update_calls(d)
                case NotifyGUI.WSJTX_STATUS:
                    self.update_rx_tx(d.transmitting, d.tx_msg)
                case NotifyGUI.GPS_OPEN:
                    self.has_gps = True
                    self.update_gps_buttons()
                case NotifyGUI.GPS_CLOSE:
                    self.gps_text.set('No GPS')
                    self.has_gps = False
                    self.update_gps_buttons()
                case NotifyGUI.GPS_MSG:
                    self.gps_text.set(d)
                case NotifyGUI.GPS_DATA:
                    self.update_time = False
                    g = 'N/A' if (dg := d['grid']) is None else dg
                    self.grid = dg
                    t = 'N/A' if (tg := d['time']) is None else '%02d:%02d:%02d' % tg
                    self.gps_text.set(f'GRID: {g}      TIME: {t}')
                    self.update_gps_buttons(self.grid, tg)
                    

    def update_gps_buttons(self, grid=None, time=None):
        if self.has_gps:
            self.time_button.configure(text = 'TIME', state='disabled' if time is None else 'normal')
            self.grid_button.configure(text = 'GRID', state='disabled' if grid is None else 'normal')                           
        else:
            self.time_button.configure(text = '', state='disabled')
            self.grid_button.configure(text = 'GPS')
            

    def update_rx_tx(self, tx, msg=''):
        self.rx_tx.set('TX: ' + msg.strip() if tx else 'RX')

 
    def do_call(self, _, entry):
        sel = entry.selection()
        if len(sel) > 0:
            index = self.lookup[entry].get(sel[0])
            if index is not None:
                msg = self.call_data[entry][index]
                self.receive.send(reply(msg))

    def update_calls(self, d):
        a = d[0] + d[1] + d[2]
        if len(a) == 0:
            return
        if chg := (a[0].time != self.last_decode):
            self.last_decode = a[0].time
##        if (chg):
##            print('new cycle')
        self.last_decode = a[0].time
        for (d, e) in zip(d, (self.calls_pota, self.calls_me, self.calls_cq)):
            self.update_call_entry(d, e, chg)

    def update_call_entry(self, d, e, chg):
        if (chg):
            self.call_data[e] = []
            self.lookup[e] = {}
            for item in e.get_children():
                e.delete(item)
        l = len(self.call_data[e])
        self.call_data[e] += d
        for i,j in enumerate(d):
            k = e.insert(parent='', index='end', values=(f"{j.snr:3}", j.message,))
            self.lookup[e][k] = i + l
            
    def check_dark(self):
        cur_dark = isDark()
        if cur_dark != self.last_dark:
            self.last_dark = cur_dark
            self.style.theme_use("forest-" + ("dark" if cur_dark else "light"))
        self.after_task = self.after(4_000, self.check_dark)

    def start_others(self):
        self.gps.start()
        self.wsjtx.start()

    def start(self):
        self.wsjtx = WSJTX()
        self.gps = GPS()
        self.after_idle(self.start_others)
        self.mainloop()
        manager.running = False
        if self.after_task is not None:
            self.after_cancel(self.after_task)
        self.destroy()
        self.wsjtx.stop()
        self.gps.stop()

if __name__ == '__main__':
    Main()
