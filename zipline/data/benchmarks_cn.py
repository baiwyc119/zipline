from zipline.utils.calendars import get_calendar
import tushare as ts

def get_benchmark_returns(symbol, start_date, end_date):
    """
    Get a Series of benchmark returns from Google Finance.
    Returns a Series with returns from (start_date, end_date].
    start_date is **not** included because we need the close from day N - 1 to
    compute the returns for day N.
    """

    print("benchmark_cn symbol is %s"%symbol)

    if symbol == "^GSPC":
        symbol = "spy"

    #print(symbol, start_date, end_date)
    # benchmark_frame = web.DataReader(symbol, 'google', start_date, end_date).sort_index()

    benchmark_frame = ts.get_h_data(
        symbol,
        start=start_date.strftime("%Y-%m-%d") if start_date != None else None,
        end=end_date.strftime("%Y-%m-%d") if end_date != None else None,
        retry_count=5,
        pause=1
    ).sort_index()
    calendar = get_calendar("SHSZ")
    sessions = calendar.sessions_in_range(start_date, end_date)
    df = benchmark_frame.reindex(
        sessions.tz_localize(None),
        copy=False,
        # ).fillna(0.0)["Close"].tz_localize('UTC').pct_change(1).iloc[1:]
    ).fillna(0.0)["close"].tz_localize('UTC').pct_change(1).iloc[1:]

    # x = df["Close"].sort_index().tz_localize('UTC').pct_change(1).iloc[1:]
    return df
