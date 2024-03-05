from settings import settings
from gui import Gui
from wsjtx import WSJTX

if settings.platform == 'win32':
    from gps import GPS
else:
    from gps_udp import GPS

def main():
    wsjtx = WSJTX()
    gps = GPS()
    
    wsjtx.start()
    gps.start()
    Gui().start(wsjtx, gps)
    
    wsjtx.stop()
    gps.stop()
    
        
if __name__ == '__main__':
    main()
