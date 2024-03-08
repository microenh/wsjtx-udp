import os
from datetime import datetime, timezone
from utility import calc_shift

APP_NAME = 'wsjtx-udp'

class Settings:
    
    def __init__(self):

        # compute data folder in user local storage
        self.df = os.path.join(os.getenv('LOCALAPPDATA') or '', APP_NAME)
        if not os.path.exists(self.df):
            os.makedirs(self.df)

        self.dbn = os.path.join(self.df, APP_NAME + '.sqlite')
        self.adifn = os.path.join(self.df, APP_NAME + '.adi')
        self.inin = os.path.join(self.df, APP_NAME + '.ini')

        self.platform = ''
        if os.name == 'nt':
            self.platform = 'win32'
        elif os.name == 'posix':
            if 'rpi' in os.uname().release:
                self.platform = 'rpi'
            else:
                self.platform = 'posix'
                
        if self.platform == 'win32':
            self.gps_address = 'COM5'
        else:
            self.gps_address = ('127.0.0.1', 2947)
            
        self.wsjtx_address = ('127.0.0.1', 2237)
        
        self.park = ''
        self.shift = ''
        self.band = 0
        self.mode = None

    def update_status(self, d):
        self.band = d.dial_freq // 1_000_000
        n = datetime.now(timezone.utc)
        self.ordinal = n.toordinal()
        self.de_call = d.de_call.upper()
        self.grid = d.de_grid
        self.shift = calc_shift(self.grid, n.hour) if settings.park > '' else ''
        self.mode = d.mode
        
          
settings = Settings()

