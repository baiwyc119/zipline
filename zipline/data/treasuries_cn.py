# encoding:utf-8

#中国国债相关数据

from operator import itemgetter
import re

import numpy as np
import pandas as pd
import datetime
import requests
from io import BytesIO, StringIO


get_unit_and_periods = itemgetter('unit', 'periods')

DONWLOAD_URL = "http://yield.chinabond.com.cn/cbweb-mn/yc/downYearBzqx?year=%s&&wrjxCBFlag=0&&zblx=txy&ycDefId=%s"
YIELD_MAIN_URL = 'http://yield.chinabond.com.cn/cbweb-mn/yield_main'


def parse_treasury_csv_column(column):
    """
    Parse a treasury CSV column into a more human-readable format.

    Columns start with 'RIFLGFC', followed by Y or M (year or month), followed
    by a two-digit number signifying number of years/months, followed by _N.B.
    We only care about the middle two entries, which we turn into a string like
    3month or 30year.
    """
    column_re = re.compile(
        r"^(?P<prefix>RIFLGFC)"
        "(?P<unit>[YM])"
        "(?P<periods>[0-9]{2})"
        "(?P<suffix>_N.B)$"
    )

    match = column_re.match(column)
    if match is None:
        raise ValueError("Couldn't parse CSV column %r." % column)
    unit, periods = get_unit_and_periods(match.groupdict())

    # Roundtrip through int to coerce '06' into '6'.
    return str(int(periods)) + ('year' if unit == 'Y' else 'month')


def earliest_possible_date():
    """
    The earliest date for which we can load data from this module.
    """
    # The China Treasury actually has data going back further than this, but it's
    # pretty rare to find pricing data going back that far, and there's no
    # reason to make people download benchmarks back to 1950 that they'll never
    # be able to use.
    # return pd.Timestamp('2002', tz='Asia/Shanghai')
    return pd.Timestamp('1990', tz='Asia/Shanghai')

def get_data():
    cur_year = datetime.datetime.now().year
    in_package_data = range(2015, cur_year + 1)

    # download new data
    to_downloads = in_package_data
    # frist, get ycDefIds params
    response = requests.get(YIELD_MAIN_URL)

    matchs = re.search(r'\?ycDefIds=(.*?)\&', response.text)
    ycdefids = matchs.group(1)
    assert (ycdefids is not None)

    fetched_data = []
    for year in to_downloads:
        print('Downloading from ' + DONWLOAD_URL % (year, ycdefids))
        response = requests.get(DONWLOAD_URL % (year, ycdefids))
        print ("response:", response)
        fetched_data.append(BytesIO(response.content))

    # combine all data

    dfs = []

    # basedir = os.path.join(os.path.dirname(__file__), "xlsx")
    '''
    basedir = os.path.join("D:\\Anaconda2\\Lib\\site-packages\\cn_treasury_curve", "xlsx")
    print "basedir :",basedir
    for i in in_package_data:
        print os.path.join(basedir, "%d.xlsx" % i)
        dfs.append(pd.read_excel(os.path.join(basedir, "%d.xlsx" % i)))
    '''
    for memfile in fetched_data:
        dfs.append(pd.read_excel(memfile,encoding="gb2312"))

    df = pd.concat(dfs)

    return df


def get_pivot_data():
    df = get_data()

    df[u'日期'] = pd.to_datetime(df[u'日期'],format='%Y/%m/%d').tz_localize('UTC')

    return df.pivot(index=u'日期', columns=u'标准期限(年)', values=u'收益率(%)')


def insert_zipline_treasure_format():
    pivot_data = get_pivot_data()

    frame = pivot_data[[0.08, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]]


    frame.index.name = 'Time Period'
    frame.columns = ['1month', '3month', '6month', '1year', '2year', '3year', '5year', '7year', '10year', '20year',
                     '30year']

    data = frame.tz_localize('UTC') * 0.01

    data.to_csv('xxx.csv', index=False, header=True)

    print frame


    return frame

def get_treasury_data(start_date, end_date):

    return insert_zipline_treasure_format()


def dataconverter(s):
    try:
        return float(s) / 100
    except:
        return np.nan


def get_daily_10yr_treasury_data():
    """Download daily 10 year treasury rates from the Federal Reserve and
    return a pandas.Series."""
    return None
