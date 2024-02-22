from datetime import datetime, timezone
from utility import calc_shift

class Settings:
    def __init__(self):
        self.activator = False
        self.park = ''

    def update_status(self, d):
        self.band = d.dial_freq // 1_000_000
        n = datetime.now(timezone.utc)
        self.ordinal = n.toordinal()
        self.de_call = d.de_call.upper()
        self.grid = d.de_grid
        self.shift = calc_shift(self.grid, n.hour)
        self.mode = d.mode
        
          
settings = Settings()
