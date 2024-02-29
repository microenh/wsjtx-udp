import os
import tkinter as tk
from tkinter import scrolledtext, ttk

from darkdetect import isDark
from PIL import Image, ImageTk
from settings import settings
from tx_msg import reply, location, free_text, halt_tx
from utility import settimefromgps

from event import NotifyGUI
from manager import manager



class Gui(tk.Tk):
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
        self.time = ''
        self.grid = ''
        self.has_gps = False
        self.update_time = False

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
        self.check_dark()

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
        self.time_button = ttk.Button(f, command=self.do_time_button)
        self.time_button.pack(side='right')
        self.grid_button = ttk.Button(f, command=self.do_grid_button)
        self.grid_button.pack(side='right', padx=(0,10))

    def do_grid_button(self):
        if not self.has_gps:
            self.gps.start()
            return
        if self.grid > '':
            self.receive.send(location(self.grid))
            self.gps_text.set(f'GRID set to {self.grid}')
            

    def do_time_button(self):
        if self.time > '':
            self.update_time = True


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
            match id_:
                case NotifyGUI.QUIT:
                    self.quit()
                case NotifyGUI.HB:
                    pass
                case NotifyGUI.CALLS:
                    self.update_calls(d)
                case NotifyGUI.STATUS:
                    self.update_rx_tx(d.transmitting, d.tx_msg)
                case NotifyGUI.GPS_OPEN:
                    self.has_gps = True
                    self.time = ''
                    self.grid = ''
                    self.update_gps_buttons()
                case NotifyGUI.GPS_CLOSE:
                    self.gps_text.set('No GPS')
                    self.has_gps = False
                    self.time = ''
                    self.grid = ''
                    self.update_gps_buttons()
                case NotifyGUI.GPGGA:
                    do_update = self.update_time
                    self.update_time = False
                    self.grid = d['grid']
                    self.time = d['time']
                    if do_update and self.time > '':
                        self.gps_text.set('Time updated')
                        settimefromgps(d['utctime'])
                    else:
                        self.set_gps_text()
                    self.update_gps_buttons()
                    

    def set_gps_text(self):
        t = a if (a:=self.time) > '' else 'N/A'
        g = a if (a:=self.grid) > '' else 'N/A'
        self.gps_text.set(f'GRID: {g}      TIME: {t}')
        

    def update_gps_buttons(self):
        if self.has_gps:
            self.time_button.configure(text = 'TIME', state='normal' if (self.time > '') else 'disabled')
            self.grid_button.configure(text = 'GRID', state='normal' if (self.grid > '') else 'disabled')                           
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
        self.after(10, self.check_dark)

    def start(self, receive, gps):
        self.receive = receive
        self.gps = gps
        self.mainloop()
        manager.running = False
        self.destroy()

if __name__ == '__main__':
    Gui().start(None, None)
##    from main import main
##    main()
