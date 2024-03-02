#!  /home/pi/Developer/wsjtx-udp/.venv/bin/python
from gui import Gui
from receive import Receive
from gps import GPS

def main():
    receive = Receive()
    gps = GPS()
    
    receive.start()
    gps.start()
    Gui().start(receive, gps)
    
    receive.stop()
    gps.stop()
    
        
if __name__ == '__main__':
    main()
