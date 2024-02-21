"""store logged contacts"""
import os
import sqlite3
from datetime import datetime, timezone

from datafolder import data_folder
from utility import lon_lat
from settings import settings

wsjtx_db = None

class WSJTXDB:
    def __init__(self):
        FILENAME = 'wsjtxDB.sqlite'
        CREATE_TABLES = ("""
            create table if not exists qsos (
                time_off int,
                dx_call text,
                dx_grid text,
                tx_freq int,
                mode text,
                rst_sent text,
                rst_recv text,
                tx_power text,
                comments text,
                name text,
                time_on real,
                op_call text,
                my_call text,
                my_grid text,
                ex_sent text,
                ex_recv text,
                adif_md text,
                ordinal_on int,
                band int,
                park text,
                shift text
            );""",
            """
            create unique index if not exists activator on qsos (
                dx_call,
                mode,
                ordinal_on,
                band,
                park,
                shift);
            """,
            """
            create unique index if not exists hunter on qsos (
                dx_call,
                mode,
                ordinal_on,
                band);
            """,
        )
        self.dbn = os.path.join(data_folder(), FILENAME)

        with sqlite3.connect(self.dbn) as con:
            for i in CREATE_TABLES:
                con.execute(i)

    def exists_activator(self, dx_call, d):
        QUERY = """select exists(
            select 1 from qsos
                where dx_call=?
                and mode=?
                and ordinal_on=?
                and band=?
                and park=?
                and shift=?
            )"""
        with sqlite3.connect(self.dbn) as con:
            return con.execute(QUERY, (
                dx_call,
                d['mode'],
                settings.ordinal,
                settings.band,
                settings.park_name.get(),
                settings.shift,
            )).fetchone()        

    def exists_hunter(self, dx_call, d):
        QUERY = """select exists(
            select 1 from qsos
                where dx_call=?
                and mode=?
                and ordinal_on=?
                and band=?
                and park=''
            )"""
        with sqlite3.connect(self.dbn) as con:
            return con.execute(QUERY, (
                dx_call,
                settings.mode,
                settings.ordinal,
                settings.band,
            )).fetchone()

    def add(self, d):
        QUERY = """insert or replace into qsos(
                time_off,
                dx_call,
                dx_grid,
                tx_freq,
                mode,
                rst_sent,
                rst_recv,
                tx_power,
                comments,
                name,
                time_on,
                op_call,
                my_call,
                my_grid,
                ex_sent,
                ex_recv,
                adif_md,
                ordinal_on,
                band,
                park,
                shift
        ) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        
        with sqlite3.connect(self.dbn) as con:
            con.execute(QUERY, (
                d['time_off'].timestamp(),
                d['dx_call'],
                d['dx_grid'],
                d['tx_freq'],
                d['mode'],
                d['rst_sent'],
                d['rst_recv'],
                d['tx_power'],
                d['comments'],
                d['name'],
                d['time_on'].timestamp(),
                d['op_call'],
                d['my_call'],
                d['my_grid'],
                d['ex_sent'],
                d['ex_recv'],
                d['adif_md'],
                settings.ordinal,
                settings.band,
                settings.park.get(),
                settings.shift,
            ))
        
def get_wsjtx_db():
    global wsjtx_db
    if wsjtx_db is None:
        wsjtx_db = WSJTXDB()
    return wsjtx_db

