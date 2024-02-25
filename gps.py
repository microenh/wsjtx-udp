from serial import Serial, SerialException, PortNotOpenError
import threading
from event import *
from utility import grid_square, timefromgps, todec
from settings import settings

class GPS:
    def __init__(self, gui):
        self.gui = gui
        self.running = True
        try:
            self.ser = Serial(settings.GPS_PORT, 9600, timeout=1, write_timeout=1)
        except Exception as e:
            self.send(NotifyGUI.QUIT)

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        try:
            self.thread.join()
        except:
            pass

    def write(self, data):
        try:
            self.ser.write(data)
        except:
            self.send(NotifyGUI.QUIT)

    def send(self, id_, data=None):
        if settings.running:
            with lock:
                notify_queue.put((id_, data))
                self.gui.event_generate(NOTIFY_GUI, when='tail')

    def process(self, data):
        a = data.strip().split(',')
        match a[0]:
            case '$GPGGA':
                time = timefromgps(a[1]).__str__()
                lat = todec(a[2],a[3])
                lon = todec(a[4],a[5])
                grid = grid_square(lon, lat)[:6]
                fix = int(a[6])
                sats = a[7]
                self.send(NotifyGUI.GPGGA, {'time': time,
                                            'grid': grid,
                                            'fix':  fix,
                                            'sats': sats})
            

    def run(self):
        while settings.running:
            try:
                try:
                    data = self.ser.read_until(b'\r').decode('utf-8')
                except:
                    pass
                self.process(data)
            except PortNotOpenError:
                self.send(NotifyGUI.QUIT)

if __name__ == '__main__':
    from main import main
    main()
