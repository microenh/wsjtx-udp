from threading import Thread
from serial import Serial, SerialException, PortNotOpenError, LF

from manager import manager

class SerialBase:
    def __init__(self, port, baud, expected=LF):
        self.ser = Serial(None,
                          baud,
                          timeout=2.0,
                          write_timeout=1.0)
        self.expected = expected
        self.ser.port = port
        self.thread = Thread()
        self.thread.start()

    def start(self):
        if self.thread.is_alive():
            return
        try:
            self.ser.open()
            self.thread = Thread(target=self.run)
            self.thread.start()
            self.report_serial_open()
        except SerialException:
            self.report_serial_close()
            
    def push(self, id_, data=None):
        manager.push(id_, data)

    def stop(self):
        self.ser.close()
        self.running = False
        self.thread.join()

    def write(self, data):
        if self.ser.is_open:
            try:
                with manager.lock:
                    self.ser.write(data)
            except SerialException:
                self.ser.close()
                self.report_serial_close()

    def run(self):
        while manager.running:
            if not self.ser.is_open:
                break
            try:
                data = self.ser.read_until(self.expected)
                if data[-1:] != self.expected:
                    print('runt')
                    continue
                data = data.decode('utf-8')
                self.process(data)
            except SerialException:
                self.ser.close()
                self.report_serial_close()
                break


if __name__ == '__main__':
    from main import main
    main()
