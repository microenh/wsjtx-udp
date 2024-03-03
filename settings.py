import os
from datetime import datetime, timezone
from utility import calc_shift


class Settings:
    
    def __init__(self):
        self.platform = ''
        if os.name == 'nt':
            self.platform = 'win32'
        elif os.name == 'posix':
            if 'rpi' in os.uname().release:
                self.platform = 'rpi'
            else:
                self.platform = 'posix'
        if self.platform == 'win32':
            self.gps_port = 'COM5'
        else:
            self.gps_port = '/dev/ttyACM0'
        self.wsjt_port = 2237
        self.host = '224.0.0.1'    
        self.capture_data = None  # set to None (no capture) or filename
        self.db_name = 'wsjtxDB.sqlite'
        self.adi_name = 'wsjtx.adi'
        self.park = ''
        self.mode = None

    def update_status(self, d):
        self.band = d.dial_freq // 1_000_000
        n = datetime.now(timezone.utc)
        self.ordinal = n.toordinal()
        self.de_call = d.de_call.upper()
        self.grid = d.de_grid
        self.shift = calc_shift(self.grid, n.hour)
        if d.mode != self.mode:
            self.mode = d.mode

    @property
    def activator(self):
        return len(self.park) > 0
        
          
settings = Settings()
