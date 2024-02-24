import os
import tkinter as tk
from tkinter import scrolledtext, ttk

from darkdetect import isDark
from PIL import Image, ImageTk
from settings import settings
from tx_msg import reply, location, free_text

from event import UPDATE_CALLS, UPDATE_STATUS


class Gui(tk.Tk):
    """Main class more"""
    LOGO = os.path.join(os.path.dirname(__file__), "Logo.png")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screenName = ':0.0'
        if os.environ.get('DISPLAY', '') == '':
            os.environ.__setitem__('DISPLAY', ':0.0')
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.lookup = {}
        self.call_data = []
        self.setup_variables()
        self.setup_theme()
        self.layout()

    def setup_variables(self):
        self.park = tk.StringVar()
        self.location = tk.StringVar()
        self.park.trace_add('write', self.trace_park)
        self.rx_tx = tk.StringVar()
        
    def trace_park(self, _a,_b,_c):
        self.park.set(x := self.park.get().upper())
        settings.park = x
        settings.activator = len(x) > 0

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
        
        # self.after_idle(lambda: self.eval('tk::PlaceWindow . center'))
        
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='y')
        ttk.Label(main_frame, image=self.image).pack()
        
        bg = ttk.Frame(main_frame)
        bg.pack(padx=10)

        f = ttk.Frame(bg)
        f.pack(expand=True, fill='x')
        ttk.Label(f, textvariable=self.rx_tx).pack(fill='x', anchor='center', pady=(0,10))
        
        f = ttk.Frame(bg)
        f.pack(expand=True, fill='y')
        self.calls = ttk.Treeview(f, height=10, show='tree')
        self.calls.pack(side='left',)
        vsb = ttk.Scrollbar(f, orient="vertical", command=self.calls.yview)
        vsb.pack(expand=True, fill='y')
        

        self.calls.configure(yscrollcommand=vsb.set)

        self.calls['columns'] = ('SNR','Message')
        self.calls.column('#0', width=0, stretch='no')
        self.calls.column('SNR', width=30, stretch='no')
        self.calls.column('Message', width=250, stretch='yes')

        self.calls.bind('<Double-1>', self.do_call)
        self.calls.bind('<Return>', self.do_call)

        f = ttk.Frame(bg)
        f.pack(fill='x', pady=10)
        ttk.Label(f, text="Park").pack(side='left')
        park = ttk.Entry(f, textvariable=self.park)
        park.pack(fill='x', padx=(10,0))
        
        f = ttk.Frame(bg)
        f.pack(fill='x', pady=10)
        ttk.Label(f, text="My Grid").pack(side='left')
        park = ttk.Entry(f, textvariable=self.location)
        park.pack(fill='x', padx=(10,0))
        park.bind('<Return>', self.update_grid)
        
        self.bind(UPDATE_CALLS, self.update_calls)
        self.bind(UPDATE_STATUS, self.update_status)

    def update_status(self, e):
        self.rx_tx.set(e.VirtualEventData)

    def update_grid(self, _):
        self.receive.send(location(self.location.get().upper()))
        # self.receive.send(free_text(self.location.get().upper(), True))
 
    def do_call(self, _):
        sel = self.calls.selection()
        if len(sel) > 0:
            index = self.lookup.get(sel[0])
            if index is not None:
                msg = self.call_data[index]
                # print(msg)
                self.receive.send(reply(msg))

    def update_calls(self, e):
        self.call_data = e.VirtualEventData
        for item in self.calls.get_children():
            self.calls.delete(item)

        self.lookup = {}
        for i,j in enumerate(self.call_data):
            k = self.calls.insert(parent='', index=i, values=(f"{j.snr:3}", j.message,))
            self.lookup[k] = i
            
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
    Gui().run(None)
