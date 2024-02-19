#! C:\Users\mark\Developer\Python\wsjtx-udp\.venv\scripts\pythonw.exe
from gui import Gui
from receive import Receive

def main():
    gui = Gui()
    receive = Receive(gui)
    receive.start()
    gui.run(receive)
    receive.stop()
        
if __name__ == '__main__':
    main()
 
