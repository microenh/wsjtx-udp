from struct import unpack_from, calcsize
from datetime import datetime, timedelta, timezone

def parse_base(fmt, d, index):
    r = unpack_from(fmt, d, index[0])[0]
    index[0] += calcsize(fmt)
    return r

def to_datetime(jday, msec, timespec, offset):
    dt = (datetime.fromordinal(jday - 1721425) + timedelta(seconds=msec/1000))
    match timespec:
        case 0:
            dt = dt.astimezone()
        case 1|2:
            dt = dt.replace(tzinfo=timezone(timedelta(seconds=offset)))    
    return dt

qbool = lambda d, index: parse_base('?', d, index)
qint8 = lambda d, index: parse_base('b', d, index)
quint8 = lambda d, index: parse_base('B', d, index)
qint32 = lambda d, index: parse_base('>i', d, index)
quint32 = lambda d, index: parse_base('>I', d, index)
qint64 = lambda d, index: parse_base('>q', d, index)
quint64 = lambda d, index: parse_base('>Q', d, index)
qdouble = lambda d, index: parse_base('>d', d, index)

def qdatetime(d, index):
    return(quint64(d, index),
           qint32(d, index),
           (ts := qint8(d, index)),
           (qint32(d, index) if ts==2 else 0))

def qutf8(d, index):
    i = 0 if (m:=quint32(d, index)) == 0xffffffff else m
    index[0] = (o:=index[0]) + i
    return '' if i == 0 else d[o:index[0]].decode()
                 
def header(d, index):
    return {
        'magic':  quint32(d, index),
        'schema': quint32(d, index),
        'msg_id': quint32(d, index),
        'id':     qutf8(d, index),        
    }

def heartbeat(d, index):
    return {
        'max_schema': quint32(d, index),
        'version':    qutf8(d, index),
        'revision':   qutf8(d, index),
    }

def status(d, index):
    return {
        'dial_freq':    quint64(d, index),
        'mode':         qutf8(d, index),
        'dx_call':      qutf8(d, index),
        'report':       qutf8(d, index),
        'tx_mode':      qutf8(d, index),
        'tx_enabled':   qbool(d, index),
        'transmitting': qbool(d, index),
        'decoding':     qbool(d, index),
        'rx_df':        quint32(d, index),
        'rx_df':        quint32(d, index),
        'de_call':      qutf8(d, index),
        'de_grid':      qutf8(d, index),
        'dx_grid':      qutf8(d, index),
        'tx_watchdog':  qbool(d, index),
        'sub_mode':     qutf8(d, index),
        'fast_mode':    qbool(d, index),
        'spec_mode':    quint8(d, index),
        'freq_tol':     quint32(d, index),
        'tr_period':    quint32(d, index),
        'conf_name':    qutf8(d, index),
        'tx_msg':       qutf8(d, index),
    }

def decode(d, index):
    return {
        'new':        qbool(d, index),
        'time':       quint32(d, index),
        'snr':        qint32(d, index),
        'delta_time': qdouble(d, index),
        'delta_freq': quint32(d, index),
        'mode':       qutf8(d, index),
        'message':    qutf8(d, index),
        'low_conf':   qbool(d, index),
        'off_air':    qbool(d, index),
    }

def clear(d, index):
    if len(d) > index[0]:
        return {
            'window': quint8(d, index)
        }
    else:
        return {}

def reply(d, index):
    return {
        'time': quint32(d, index),
        'snr': qint32(d, index),
        'delta_time': qdouble(d, index),
        'delta_freq': qint32(d, index),
        'mode': qutf8(d, index),
        'message': qutf8(d, index),
        'low_conf': qbool(d, index),
        'modifiers': quint8(d, index),
    }

def log(d, index):
    return {
        'time_off': qdatetime(d, index),
        'dx_call':  qutf8(d, index),
        'dx_grid':  qutf8(d, index),
        'tx_freq':  quint64(d, index),
        'mode':     qutf8(d,index),
        'rst_sent': qutf8(d, index),
        'rst_recv': qutf8(d, index),
        'tx_power': qutf8(d, index),
        'comments': qutf8(d, index),
        'name':     qutf8(d, index),
        'time_on':  qdatetime(d, index),
        'op_call':  qutf8(d, index),
        'my_call':  qutf8(d, index),
        'my_grid':  qutf8(d, index),
        'ex_sent':  qutf8(d, index),
        'ex_recv':  qutf8(d, index),
        'adif_md':  qutf8(d, index),
    }

def close(d, index):
    return {}

def replay(d, index):
    return {}

def halt_tx(d, index):
    return {
        'auto_tx_only': qbool(d, index),
    }

def free_text(d, index):
    return {
        'text': qutf8(d, index),
        'send' : qbool(d, index),
    }

def wspr(d, index):
    return {
        'new':        qbool(d, index),
        'time':       quint32(d, index),
        'snr':        qint32(d, index),
        'delta_time': qdouble(d, index),
        'freq':       quint64(d, index),
        'drift':      quint32(d, index),
        'callsign':   qutf8(d, index),
        'grid':       qutf8(d, index),
        'power':      qint32(d, index),
        'off_air':    qbool(d, index),
    }

def location(d, index):
    return {
        'location': qutf8(d, index),
    }

def adif(d, index):
    return {
        'text': qutf8(d, index),
    }

def highlight_callsign(d, index):
    return {
        'call': qutf8(d, index),
        'bg': qcolor(d, index),
        'fg': qcolor(d, index),
        'last_only': qbool(d, index),
    }

def switch_conf(d, index):
    return {
        'conf_name': qutf8(d, index)
    }

def configure(d, index):
    return{
        'mode': qutf8(d, index),
        'freq_tol': quint32(d, index),
        'submode': qutf8(d, index),
        'fastmode': qbool(d, index),
        'tr_period': quint32(d, index),
        'rx_df': quint32(3, index),
        'dx_call': qutf8(d, index),
        'dx_grid': qutf8(d, index),
        'gen_msg': qbool(d, index),
    }

decoders = (
    heartbeat,
    status,
    decode,
    clear,
    reply,
    log,
    close,
    replay,
    halt_tx,
    free_text,
    wspr,
    location,
    adif,
    highlight_callsign,
    switch_conf,
    configure,
)

def parse(d):
    class Data:
        def __init__(self, a):
            self.__dict__ = a
    index = [0]
    r = header(d, index)
    r['raw'] = d
    r.update(decoders[r['msg_id']](d, index))
    return Data(r)


if __name__ == '__main__':
    from sample_data.small_sample import SAMPLE_DATA
    for i in SAMPLE_DATA.values():
        print(parse(i).msg_id)
