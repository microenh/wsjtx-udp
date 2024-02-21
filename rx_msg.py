from struct import unpack_from
from datetime import datetime, timedelta, timezone

def qbool(d, index):
    r = unpack_from('?', d, index[0])[0]
    index[0] += 1
    return r

def qint8(d, index):
    r = unpack_from('b', d, index[0])[0]
    index[0] += 1
    return r

def quint8(d, index):
    r = unpack_from('B', d, index[0])[0]
    index[0] += 1
    return r

def qint32(d, index):
    r = unpack_from('>i', d, index[0])[0]
    index[0] += 4
    return r

def quint32(d, index):
    r = unpack_from('>I', d, index[0])[0]
    index[0] += 4
    return r

##def qint64(d, index):
##    r = unpack_from('>q', d, index[0])[0]
##    index[0] += 8
##    return r

def quint64(d, index):
    r = unpack_from('>Q', d, index[0])[0]
    index[0] += 8
    return r

def qdouble(d, index):
    r = unpack_from('>d', d, index[0])[0]
    index[0] += 8
    return r

def qdatetime(d, index):
    jday = quint64(d, index)
    msec = qint32(d, index)
    timespec = qint8(d, index)
    if timespec == 2:
        offset = qint32(d, index)
    else:
        offset = 0
    dt = (datetime.fromordinal(jday - 1721425) + timedelta(seconds=msec/1000))
    match timespec:
        case 0:
            dt = dt.astimezone()
        case 1|2:
            dt = dt.replace(tzinfo=timezone(timedelta(seconds=offset)))
    
    return dt
    
def qutf8(d, index):
    s_len = quint32(d, index)
    if s_len == 0xffffffff:
        s_len = 0
    if s_len == 0:
        return ''
    else:
        old_index = index[0]
        index[0] += s_len
        return d[old_index:old_index+s_len].decode()

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
    index = [0]
    r = header(d, index)
    r['raw'] = d
    r.update(decoders[r['msg_id']](d, index))
    return r


if __name__ == '__main__':
    from sample_data import SAMPLE_DATA
    msgs = {}
    for i in SAMPLE_DATA:
        p = parse(i)
        msgs[m] = msgs.get((m:=p['msg_id']),0) + 1
        #print(parse(i))
    print(msgs)
