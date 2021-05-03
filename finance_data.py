import yfinance as yf

def get_yfinance_data(ticker, period, interval):
    return yf.Ticker(ticker).history(period=period, interval=interval)


def calculate_ichimoku(data, tf):
    if tf == '1d':
        multiplier = 24
    elif tf == '4h':
        multiplier = 4
    else:
        multiplier = 1

    if data.empty:
        return False

    cl_coef = 9 * multiplier
    bl_coef = 26 * multiplier
    ssb_coef = 52 * multiplier

    c_cl = (data.tail(cl_coef)['High'].max() + data.tail(cl_coef)['Low'].min()) / 2
    c_bl = (data.tail(bl_coef)['High'].max() + data.tail(bl_coef)['Low'].min()) / 2
    c_ssa = (c_cl + c_bl) / 2
    c_ssb = (data.tail(ssb_coef)['High'].max() + data.tail(ssb_coef)['Low'].min()) / 2

    p_cl = (data.tail(cl_coef + 1).head(cl_coef)['High'].max() + data.tail(cl_coef + 1).head(cl_coef)['Low'].min()) / 2
    p_bl = (data.tail(bl_coef + 4).head(bl_coef)['High'].max() + data.tail(bl_coef + 4).head(bl_coef)['Low'].min()) / 2
    p_ssa = (p_cl + p_bl) / 2
    p_ssb = (data.tail(ssb_coef + 24).head(ssb_coef)['High'].max() + data.tail(ssb_coef + 24).head(ssb_coef)['Low'].min()) / 2

    if c_bl > p_bl and c_bl > c_ssb:
        if data.tail(1)['Close'][0] > c_bl and c_bl > c_ssb and (c_ssb > p_ssb or (c_ssb == p_ssb and c_ssa > p_ssa)):
            return 1
    elif c_bl < p_bl and c_bl < c_ssb:
        if data.tail(1)['Close'][0] < c_bl and c_bl < c_ssb and (c_ssb < p_ssb or (c_ssb == p_ssb and c_ssa < p_ssa)):
            return -1
    return 0


def get_data(ticker):
    data = get_yfinance_data(ticker, '52d', '1h')
    minute_data = get_yfinance_data(ticker, '2d', '30m')

    data1d = calculate_ichimoku(data, '1d')
    data4h = calculate_ichimoku(data, '4h')
    data1h = calculate_ichimoku(data, '1h')
    data30m = calculate_ichimoku(minute_data, '1h')
    if data1h != 0 and (data1d == data1h or data4h == data1h):
        trending = 1
    else:
        trending = 0

    return {
        'Ticker': [ticker],
        'Daily': [data1d],
        '4h': [data4h],
        '1h': [data1h],
        '30m': [data30m],
        'Data': [data],
        'Trending': [trending]
    }
