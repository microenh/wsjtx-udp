def lon_lat(grid_square):
    """
    convert grid square to longitude and latitude
    grid_square: AA99aa99AA or any 2,4,6,8 character subset
    """
    DIVISIONS = (
        ( 1, ord('A')),
        (10, ord('0')),
        (24, ord('a')),
        (10, ord('0')), 
        (24, ord('A'))
    )
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

if __name__ == '__main__':
    for i in (
        ('PM85kh', 'rrrrrrrrrlllllllleeeeeer'),  # Japan
        ('DM07kp', 'rrlllllllleeeeeerrrrrrrr'),  # California     
        ('EM89hu', 'lllllllleeeeeerrrrrrrrrr'),  # Ohio
        ('IO91wm', 'lleeeeeerrrrrrrrrrllllll'),  # UK -longitude
        ('JO01ir', 'lleeeeeerrrrrrrrrrllllll'),  # UK +longitude
        ('KO01hr', 'leeeeeerrrrrrrrrrlllllll'),  
        ('KO21pu', 'eeeeeerrrrrrrrrrllllllll'),
        ('KN89vw', 'eeeeerrrrrrrrrrlllllllle'),  # Ukraine UR-0025
    ):
        r = ''.join([calc_shift(i[0], hr) for hr in range(24)])
        print(i[0], r==i[1])
