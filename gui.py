import os
import tkinter as tk
from tkinter import scrolledtext, ttk

from darkdetect import isDark
from PIL import Image, ImageTk
from settings import settings
from tx_msg import reply, location, free_text, halt_tx

from event import *


class Gui(tk.Tk):
    """Main class more"""
    LOGO = os.path.join(os.path.dirname(__file__), "Logo.png")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screenName = ':0.0'
        if os.environ.get('DISPLAY', '') == '':
            os.environ.__setitem__('DISPLAY', ':0.0')
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.bind(NOTIFY_GUI, self.do_notify)

        # self.after_idle(lambda: self.eval('tk::PlaceWindow . center'))
        self.last_decode = None
        self.setup_variables()
        self.setup_theme()
        self.layout()

    def setup_variables(self):
        self.location = tk.StringVar()
        self.rx_tx = tk.StringVar()
        self.update_rx_tx(False)
    
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

##        f = ttk.Frame(bg)
##        f.pack(fill='x', pady=10)
##        ttk.Label(f, text="My Grid").pack(side='left')
##        park = ttk.Entry(f, textvariable=self.location)
##        park.pack(fill='x', padx=(10,0))
##        park.bind('<Return>', self.update_grid)


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
            try:
                id_, d = notify_queue.get_nowait()
                match id_:
                    case NotifyGUI.CALLS:
                        self.update_calls(d)
                    case NotifyGUI.STATUS:
                        self.update_rx_tx(d.transmitting, d.tx_msg)
            except Empty:
                break
            

    def update_rx_tx(self, tx, msg=''):
        self.rx_tx.set('TX: ' + msg.strip() if tx else 'RX')

    def update_grid(self, _):
        # self.receive.send(location(self.location.get().upper()))
        # self.receive.send(free_text(self.location.get().upper(), True))
        # self.rx_tx.set(self.location.get())
        ...
 
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

    def run(self, receive):
        self.receive = receive
        self.mainloop()
        self.destroy()

if __name__ == '__main__':
##    Gui().run(None)
    from main import main
    main()
