#! C:\Users\mark\Developer\Python\wsjtx-udp\.venv\scripts\pythonw.exe
from gui import Gui
from receive import Receive
from gps import GPS
from settings import settings

def main():
    gui = Gui()
    receive = Receive(gui)
    gps = GPS(gui)
    receive.start()
    gps.start()
    gui.run(receive)
    settings.running = False
    receive.stop()
    gps.stop()
        
if __name__ == '__main__':
    main()
 
