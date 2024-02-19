import os
import tkinter as tk
from tkinter import scrolledtext, ttk

from darkdetect import isDark
from PIL import Image, ImageTk

from event import EVENT, WSJTXEvent
from samples import SAMPLE_MESSAGES


class Gui(tk.Tk):
    """Main class more"""
    LOGO = os.path.join(os.path.dirname(__file__), "Logo.png")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screenName = ':0.0'
        if os.environ.get('DISPLAY', '') == '':
            os.environ.__setitem__('DISPLAY', ':0.0')
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.bind(EVENT, self.do_event)

        self.setup_theme()
        self.layout()

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
        self.title('POTA Helper')
        self.image = ImageTk.PhotoImage(Image.open(self.LOGO))
        self.iconphoto(False, self.image)
        
        # self.after_idle(lambda: self.eval('tk::PlaceWindow . center'))
        self.create_tk_vars()
        
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='y')
        ttk.Label(main_frame, image=self.image).pack(expand=True, pady=10)
        
        bg = ttk.Frame(main_frame)
        bg.pack(expand=True, fill='y', pady=(0,10))
        tb = ttk.Frame(bg)
        tb.pack(expand=True, fill='y')
        self.calls = ttk.Treeview(tb, height=10, show='tree')
        self.calls.pack(expand=True, side='left',  padx=(10,0))
        vsb = ttk.Scrollbar(tb, orient="vertical", command=self.calls.yview)
        vsb.pack(fill='y', expand=True)
        auto=ttk.Checkbutton(bg, text='auto-call first', variable=self.do_auto)
        auto.pack(side='left', fill='x', anchor='w', padx=10)


        self.calls.configure(yscrollcommand=vsb.set)

        self.calls['columns'] = ('SNR','Message')
        self.calls.column('#0', width=0, stretch='no')
        self.calls.column('SNR', width=30, stretch='no')
        self.calls.column('Message', width=250, stretch='yes')

        self.calls.bind('<Double-1>', self.do_call)
        self.calls.bind('<Return>', self.do_call)

        self.bind('<<UPDATE_CALLS>>', self.update_calls)

    def do_call(self, _):
        selected_items = self.calls.selection()
        if selected_items is not None:
            print (selected_items)

    def update_calls(self, e):
        for item in self.calls.get_children():
            self.calls.delete(item)
            
        for i,j in enumerate(e.VirtualEventData):
            self.calls.insert(parent='', index=i, values=(f"{j['snr']:3}", j['message'],))
            
    def create_tk_vars(self):
        self.do_auto = tk.BooleanVar()
        self.do_auto.set(False)
        

    def check_dark(self):
        cur_dark = isDark()
        if cur_dark != self.last_dark:
            self.last_dark = cur_dark
            self.style.theme_use("forest-" + ("dark" if cur_dark else "light"))
        self.after(10, self.check_dark)

    def do_event(self):
        pass

    def run(self):
        self.mainloop()
        self.destroy()

if __name__ == '__main__':
    Gui().run()
