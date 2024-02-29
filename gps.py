from serial_base import SerialBase
from utility import grid_square, timefromgps, todec
from event import NotifyGUI
from settings import settings

class GPS(SerialBase):
    def __init__(self):
        super().__init__(settings.GPS_PORT, 9600)

    def report_serial_open(self):
        # print('open')
        self.push(NotifyGUI.GPS_OPEN)        

    def report_serial_close(self):
        # print('close')
        self.push(NotifyGUI.GPS_CLOSE)        

    def process(self, data):
        a = data.strip().split(',')
        match a[0]:
            case '$GPGGA':
                if (t := a[1]) > '':
                    time = timefromgps(t).__str__()
                else:
                    time = ''
                if (la := a[2]) > '':
                    lat = todec(la, a[3])
                    lon = todec(a[4],a[5])
                    grid = grid_square(lon, lat)[:6]
                else:
                    grid = ''
##                fix = int(a[6])
##                sats = int(a[7])
                self.push(NotifyGUI.GPGGA, {'time': time,
                                            'grid': grid,
                                            'utctime': t,
##                                            'fix':  fix,
##                                            'sats': sats
                                            })

if __name__ == '__main__':
    from main import main
    main()
