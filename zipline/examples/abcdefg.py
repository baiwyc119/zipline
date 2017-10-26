
from zipline.data.treasuries_cn import get_treasury_data,earliest_possible_date

from zipline.utils.calendars import get_calendar
from zipline.finance.trading import TradingEnvironment

# print earliest_possible_date()
#
#
#
# trading_calendar = get_calendar("SHSZ")
# trading_environment = TradingEnvironment(bm_symbol='000001.SS',
#                                          exchange_tz="Asia/Shanghai",
#                                          trading_calendar=trading_calendar,
#                                          asset_db_path='xxx')


def initialize(context):
    print("hello world")


def handle_data(context, data):
    print "test"


import tushare as ts

print ts.get_h_data('399106', index=True)

print    ts.get_h_data(
        '000001',
        start='2007-01-01',
        end='2017-01-01',
        retry_count=5,
        pause=1
    ).sort_index()