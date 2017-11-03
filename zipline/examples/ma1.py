start = '2014-05-28'  # 回测开始时间
end = '2016-08-08'  # 回测结束时间
benchmark = "HS300"  # 策略对标标的
universe = set_universe('HS300')
capital_base = 100000  # 起始资金
freq = 'd'  # 策略类型，'d'表示日间策略使用日线回测，'m'表示日内策略使用分钟线回测
refresh_rate = 1  # 调仓频率，表示执行handle_data的时间间隔，若freq = 'd'时间间隔的单位为交易日，若freq = 'm'时间间隔为分钟
period1 = 5
period2 = 60
commission = Commission(buycost=0.0003, sellcost=0.0013, unit='perValue')
max_history_window = 100  # 设定调取历史价格区间最大为100个交易日


def initialize(account):  # 初始化虚拟账户状态
    pass


def handle_data(account):  # 每个交易日的买入卖出指令
    # 取PE数据排序
    data = DataAPI.MktStockFactorsOneDayGet(tradeDate=account.previous_date, secID=universe,
                                            field=u"secID,tradeDate,pe", pandas="1")
    data = data.set_index('secID')
    data = data.dropna()
    data = data[data['PE'] > 0]  # pe大于0
    data = data.sort('PE')  # pe排序
    # 取PE最小的10只股票
    univ = list(data.index[:10])
    hist1 = account.get_attribute_history('closePrice', period1)  # 获取过去5个交易日的收盘价
    hist2 = account.get_attribute_history('closePrice', period2)  # 获取过去60个交易日的收盘价

    for s in account.universe:
        MA5 = hist1[s].mean()  # 计算过去5个交易日及过去60个交易日的均价
        MA60 = hist2[s].mean()
        if s in account.avail_security_position:
            if s not in univ or MA5 < MA60:
                order_pct_to(s, 0)
        # 买股票，每个股票仓位设置为10%
        if s in univ and s not in account.valid_secpos and MA5 > MA60:
            order_pct_to(s, 0.1)