import pandas as pd
import numpy as np
import talib

start = '2012-01-01'
end = '2015-09-28'
benchmark = 'HS300'
universe = set_universe('HS300')
capital_base = 1000000
refresh_rate = 5

## 使用talib计算MACD的参数
short_win = 12  # 短期EMA平滑天数
long_win = 26  # 长期EMA平滑天数
macd_win = 20  # DEA线平滑天数

stk_num = 20  # 持仓股票数量

longest_history = 100


def initialize(account):
    account.universe = universe


def handle_data(account):
    all_close_prices = account.get_attribute_history('closePrice', longest_history)