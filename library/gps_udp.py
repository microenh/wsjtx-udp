from json import loads, JSONDecodeError

from library.udp_client_base import UDPClientBase
from library.event import NotifyGUI
from library.settings import settings
from library.utility import grid_square
from library.tx_msg import location

class GPS(UDPClientBase):
    def __init__(self):
        super().__init__(settings.gps_address)
        self.message = ''
        
    def report(self, is_open):
        self.push(NotifyGUI.GPS_OPEN if is_open else NotifyGUI.GPS_CLOSE)        

    def update_grid(self, grid, wsjtx):
        if grid is not None:
            wsjtx.send(location(grid))
            self.message = f'grid set to {grid}'
        
    def process(self, data):
        for d in data.strip().split(b'\n'):
            try:
                j = loads(data)
                match j['class']:
                    case 'VERSION':
                        self.send(b'?WATCH={"enable":true,"json":true}')
                    case 'TPV':
                        if self.message > '':
                            self.push(NotifyGUI.GPS_MSG, self.message)
                            self.message = ''
                        elif 'lat' in j:
                            grid = grid_square(j['lon'], j['lat'])[:6]
                        else:
                            grid = None
                        self.push(NotifyGUI.GPS_DATA,
                              {'time': None, 'grid': grid})
            except JSONDecodeError:
                pass
                        
                
                
                    


