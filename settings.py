from datetime import datetime, timezone
from utility import calc_shift

class Settings:
    GPS_PORT = 'COM9'
    WSJTX_PORT = 2237
    HOST = '224.0.0.1'    
    CAPTURE_DATA = None  # set to None (no capture) or filename
    DB_NAME = 'wsjtxDB.sqlite'
    ADI_NAME = 'wsjtx.adi'
    PARK = ''
    
    def __init__(self):
        self.mode = None
        self.running = True

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
        return len(self.PARK) > 0
        
          
settings = Settings()
