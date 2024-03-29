"""
all the messages generated by WSTJX
key = msg_id
"""
SAMPLE_DATA = {
     0: b'\xad\xbc\xcb\xda\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x06WSJT-X'
        b'\x00\x00\x00\x03\x00\x00\x00\x052.6.1\x00\x00\x00\x066b6d74',
     1: b'\xad\xbc\xcb\xda\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x06WSJT-X'
        b'\x00\x00\x00\x00\x00\xd7\x14\xf0\x00\x00\x00\x04WSPR\x00\x00\x00\x05N7DBS'
        b'\x00\x00\x00\x03-15\x00\x00\x00\x04WSPR\x00\x00\x00\x00\x00\x03\x98\x00'
        b'\x00\x05\xdc\x00\x00\x00\x04N8ME\x00\x00\x00\x06EM89HU\x00\x00\x00\x04DM26'
        b'\x00\xff\xff\xff\xff\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00'
        b'\rHermes Lite 2\xff\xff\xff\xff',
     3: b'\xad\xbc\xcb\xda\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x06WSJT-X',
     2: b'\xad\xbc\xcb\xda\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x06WSJT-X'
        b'\x01\x02\x86\x97X\xff\xff\xff\xfa\xbf\xe9\x99\x99\xa0\x00\x00\x00\x00\x00'
        b'\x04\xbc\x00\x00\x00\x01~\x00\x00\x00\rCQ F5IXN JN23\x00\x00',
     5: b'\xad\xbc\xcb\xda\x00\x00\x00\x02\x00\x00\x00\x05\x00\x00\x00\x06WSJT-X'
        b'\x00\x00\x00\x00\x00%\x8a\xc3\x02}\xe4\xfb\x01\x00\x00\x00\x06OE7CMI\x00'
        b'\x00\x00\x04JN57\x00\x00\x00\x00\x00\xd6\xc6\xa9\x00\x00\x00\x03FT8\x00'
        b'\x00\x00\x03123\x00\x00\x00\x03321\x00\x00\x00\x012\x00\x00\x00\x07comment'
        b'\x00\x00\x00\x06George\x00\x00\x00\x00\x00%\x8a\xc3\x02}o\xcb\x01\x00\x00\x00'
        b'\x07test op\x00\x00\x00\x04N8ME\x00\x00\x00\x06EM89HU\x00\x00\x00\x07ex sent'
        b'\x00\x00\x00\x07ex recv\xff\xff\xff\xff',
     6: b'\xad\xbc\xcb\xda\x00\x00\x00\x02\x00\x00\x00\x06\x00\x00\x00\x06WSJT-X',
    10: b'\xad\xbc\xcb\xda\x00\x00\x00\x02\x00\x00\x00\n\x00\x00\x00\x06WSJT-X\x01'
        b'\x02\x8b\xdb\x00\xff\xff\xff\xee?\xb9\x99\x99\xa0\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\xd7\x1b*\x00\x00\x00\x00\x00\x00\x00\x06SQ9SVT\x00\x00\x00'
        b'\x04JN99\x00\x00\x00%\x00',
    12: b'\xad\xbc\xcb\xda\x00\x00\x00\x02\x00\x00\x00\x0c\x00\x00\x00\x06WSJT-X'
        b'\x00\x00\x01d\n<adif_ver:5>3.1.0\n<programid:6>WSJT-X\n<EOH>\n<call:6>'
        b'OE7CMI <gridsquare:4>JN57 <mode:3>FT8 <rst_sent:3>123 <rst_rcvd:3>321 <qso_date:8>'
        b'20240214 <time_on:6>113615 <qso_date_off:8>20240214 <time_off:6>113645 <band:3>'
        b'20m <freq:9>14.075561 <station_callsign:4>N8ME <my_gridsquare:6>EM89HU <tx_pwr:1>'
        b'2 <comment:7>comment <name:6>George <operator:7>test op <EOR>',
}