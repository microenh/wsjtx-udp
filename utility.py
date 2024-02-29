from datetime import datetime, time, timezone
from win32api import SetSystemTime

DIVISIONS = (
    ( 1, ord('A')),
    (10, ord('0')),
    (24, ord('a')),
    (10, ord('0')), 
    (24, ord('A'))
)
    
def grid_square(lon, lat):
    """
    lon: decimal longitude -180 .. 180 (West is negative)
    lat: decimal latitude -90 .. 90 (South is negative)
    returns 10 character string 'AA99aa99AA' (truncate for less precision)
    """
    lat += 90
    lon += 180
    lon_div = 20.0
    lat_div = 10.0

    results = []
    for div, base in DIVISIONS:
        lon_div /= div
        lat_div /= div
        results.append(chr((lo := int(lon / lon_div)) + base)
                     + chr((la := int(lat / lat_div)) + base))
        lon -= lo * lon_div
        lat -= la * lat_div
        
    return ''.join(results)

def lon_lat(grid_square):
    """
    grid_square: AA99aa99AA or any 2,4,6,8 character subset
    """
    lon = -180.0
    lat = -90.0
    lon_mult = 20.00
    lat_mult = 10.0
    for m,p in DIVISIONS:
        if len(grid_square)< 2:
            break        
        lon_mult /= m
        lat_mult /= m
        lon += lon_mult * (ord(grid_square[0]) - p)
        lat += lat_mult * (ord(grid_square[1]) - p)
        grid_square = grid_square[2:]
    return lon, lat

def timefromgps(utctime):
    try:
        utctime = float(utctime)
    except ValueError:
        utctime = 0.0
    h = int(utctime//10_000)
    utctime -= h * 10_000
    m = int(utctime//100)
    utctime -= m * 100
    s = int(utctime + 0.5)
    return time(h,m,s,0)

def todec(x,h):
    try:
        x = float(x)
    except ValueError:
        x = 0
    d = int(x//100)
    x -= d * 100
    r = d + x / 60.0
    return r if h in 'NE' else -r

_last_grid_square = None
_last_hour = None
_last_shift = ''

def calc_shift(grid_square, hour):
    """
    'e': early shift
    'l': late shift
    'r': regular shift
    grid_sqaure: at least 'AA99'
    msec: msec after midnight UTC
    """
    global _last_grid_square, _last_hour, _last_shift
    if grid_square == _last_grid_square and hour == _last_hour:
        return _last_shift
    _last_hour = hour
    _last_grid_square = grid_square
    lon, _ = lon_lat(grid_square)
    adj = int(round(lon / 15))
    hour += adj - 2
    hour %= 24
    if hour < 6:
        _last_grid_square = 'e'
    elif hour < 16:
        _last_grid_square = 'r'
    else:
        _last_grid_square = 'l'
    return _last_grid_square

def settimefromgps(utctime):
    utctime = float(utctime)
    h = int(utctime//10_000)
    utctime -= h * 10_000
    m = int(utctime//100)
    utctime -= m * 100
    s = int(utctime)
    utctime -= s
    msec = int(utctime * 1_000)
    d = datetime.now(timezone.utc)
    SetSystemTime(d.year, d.month, d.weekday(), d.day, h, m, s, msec)


if __name__ == '__main__':
##    for i in (
##        ('PM85kh', 'rrrrrrrrrlllllllleeeeeer'),  # Japan
##        ('DM07kp', 'rrlllllllleeeeeerrrrrrrr'),  # California     
##        ('EM89hu', 'lllllllleeeeeerrrrrrrrrr'),  # Ohio
##        ('IO91wm', 'lleeeeeerrrrrrrrrrllllll'),  # UK -longitude
##        ('JO01ir', 'lleeeeeerrrrrrrrrrllllll'),  # UK +longitude
##        ('KO01hr', 'leeeeeerrrrrrrrrrlllllll'),  
##        ('KO21pu', 'eeeeeerrrrrrrrrrllllllll'),
##        ('KN89vw', 'eeeeerrrrrrrrrrlllllllle'),  # Ukraine UR-0025
##    ):
##        r = ''.join([calc_shift(i[0], hr) for hr in range(24)])
##        print(i[0], r==i[1])
    settimefromgps(0)
