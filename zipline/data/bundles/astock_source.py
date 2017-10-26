#coding:utf-8

import os
import sqlite3
import pandas as pd
import numpy as np
import requests

from . import core as bundles
from zipline.utils.calendars import register_calendar_alias
from zipline.utils.cli import maybe_show_progress

ASTOCK_DB_FILE = 'data/bundles/History.db'

def _cachepath(symbol, type_):
    return '-'.join((symbol.replace(os.path.sep,'_'), type_))

@bundles.register('astock')
def astock_bundles(environ,
                  asset_db_writer,
                  minute_bar_writer,
                  daily_bar_writer,
                  adjustment_writer,
                  calendar,
                  start_session,
                  end_session,
                  cache,
                  show_progress,
                  output_dir):


    stockPath = os.path.join(os.getcwd(),ASTOCK_DB_FILE)


    if  os.path.exists(stockPath) == False :
        print("DB File %s not Exist in current path:" % stockPath)
        raise IOError

    conn = sqlite3.connect(stockPath, check_same_thread=False)

    symbols = {}

    if len(symbols) == 0:
        query = "select name from sqlite_master where type='table' order by name"
        _df = pd.read_sql(query, conn)

        for table in _df.name:
            if table.isdigit():
                symbols[table] = None

    print("stock count is %d \n"%len(symbols))

    metadata = pd.DataFrame(np.empty(len(symbols), dtype=[
        ('start_date', 'datetime64[ns]'),
        ('end_date', 'datetime64[ns]'),
        ('auto_close_date', 'datetime64[ns]'),
        ('symbol', 'object'),
    ]))


    def _pricing_iter():
        sid = 0
        with maybe_show_progress(
            symbols,
            show_progress,
            label='Fetch stocks pricing data from db:') as it, requests.session() as session:

            for symbol in it:
                path = _cachepath(symbol, 'ohlcv')
                try:
                    df = cache[path]

                except KeyError:
                    query = "select * from '%s' order by date desc" % symbol
                    df = cache[path] = pd.read_sql(sql=query, con=conn, index_col='date',parse_dates=['date']).sort_index()

                start_date = df.index[0]
                end_date = df.index[-1]

                ac_date = end_date + pd.Timedelta(days=1)

                metadata.iloc[sid] = start_date, end_date, ac_date, symbol
                new_index = ['open', 'high', 'low', 'close', 'volume']
                df = df.reindex(columns= new_index, copy=False)

                sessions = calendar.sessions_in_range(start_date, end_date)

                df = df.reindex(sessions.tz_localize(None),
                                copy=False,).fillna(0.0)

                yield sid, df

                sid += 1


    daily_bar_writer.write(_pricing_iter(), show_progress=False)

    metadata['exchange'] = "YAHOO"

    symbol_map = pd.Series(metadata.symbol.index,metadata.symbol)


    asset_db_writer.write(equities=metadata)

    print('calling asset db writer end')

    adjustment_writer.write()

    conn.close()
