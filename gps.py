from serial_base import SerialBase
from utility import grid_square, timefromgps, todec, settimefromgps

from event import NotifyGUI
from settings import settings
from tx_msg import location

class GPS(SerialBase):
    def __init__(self):
        super().__init__(settings.GPS_PORT, 9600)
        self.day = ''
        self.message = ''
        self.grid = None
        self.update_time_request = False

    def update_time(self):
        self.update_time_request = True

    def update_grid(self, grid, receive):
        if grid is not None:
            receive.send(location(grid))
            self.message = f'grid set to {grid}'
        

    def report_serial_open(self):
        # print('open')
        self.push(NotifyGUI.GPS_OPEN)        

    def report_serial_close(self):
        # print('close')
        self.push(NotifyGUI.GPS_CLOSE)        

    def process(self, data):
        a = data.strip().split(',')
        match a[0]:
            case '$GPRMC':
                _, utc, _, la, la_dir, lo, lo_dir, _, _, dt = a[:10]
                tm = timefromgps(utc)
                lat = todec(la, la_dir)
                lon = todec(lo, lo_dir)
                grid = grid_square(lon,lat)
                if grid is not None:
                    grid = grid[:6]
                if self.update_time_request:
                    self.update_time_request = False
                    self.message = settimefromgps(dt, tm)
                if self.message > '':
                    self.push(NotifyGUI.GPS_MSG, self.message)
                    self.message = ''
                else:
                    self.push(NotifyGUI.GPRMC, {'time': tm, 'grid': grid}) 

if __name__ == '__main__':
    from main import main
    main()
