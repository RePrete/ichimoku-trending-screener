import yfinance as yf

CONVERSION_LINE_CANDLES = 9
BASE_LINE_CANDLES = 26
SSB_LINE_CANDLES = 52


def get_yfinance_data(ticker, period, interval):
    return yf.Ticker(ticker).history(period=period, interval=interval)


def calculate_ichimoku(data, factor):
    if data.empty:
        return 0

    cl_coef = int(CONVERSION_LINE_CANDLES * factor)
    bl_coef = int(BASE_LINE_CANDLES * factor)
    ssb_coef = int(SSB_LINE_CANDLES * factor)

    c_cl = (data.tail(cl_coef)['High'].max() + data.tail(cl_coef)['Low'].min()) / 2
    c_bl = (data.tail(bl_coef)['High'].max() + data.tail(bl_coef)['Low'].min()) / 2
    c_ssa = (c_cl + c_bl) / 2
    c_ssb = (data.tail(ssb_coef)['High'].max() + data.tail(ssb_coef)['Low'].min()) / 2

    p_cl = (data.tail(cl_coef + int(factor)).head(cl_coef)['High'].max() +
            data.tail(cl_coef + int(factor)).head(cl_coef)['Low'].min()) / 2
    p_bl = (data.tail(bl_coef + int(factor)).head(bl_coef)['High'].max() +
            data.tail(bl_coef + int(factor)).head(bl_coef)['Low'].min()) / 2
    p_ssa = (p_cl + p_bl) / 2
    p_ssb = (data.tail(ssb_coef + int(factor)).head(ssb_coef)['High'].max() +
             data.tail(ssb_coef + int(factor)).head(ssb_coef)['Low'].min()) / 2

    # Base line up and above ssb
    # if c_bl > p_bl and c_bl > c_ssb:
    #     # Price above base line
    #     if data.tail(1)['Close'][0] > c_bl and c_bl > c_ssb:
    #         if c_ssb > p_ssb:
    #             return 1
    #         elif c_ssb == p_ssb and c_ssa > p_ssa:
    #             return 0.5
    # elif c_bl < p_bl and c_bl < c_ssb:
    #     if data.tail(1)['Close'][0] < c_bl and c_bl < c_ssb:
    #         if c_ssb < p_ssb:
    #             return -1
    #         elif c_ssb == p_ssb and c_ssa < p_ssa:
    #             return -0.5

    if c_bl > p_bl and c_bl > c_ssb:
        if data.tail(1)['Close'][0] > c_bl and c_bl > c_ssb and c_ssb > p_ssb:
            return 1
    elif c_bl < p_bl and c_bl < c_ssb:
        if data.tail(1)['Close'][0] < c_bl and c_bl < c_ssb and c_ssb < p_ssb:
            return -1
    return 0


def get_data(ticker):
    data = get_yfinance_data(ticker, '52d', '1h')

    data1d = calculate_ichimoku(data, 24)
    data4h = calculate_ichimoku(data, 4)
    data1h = calculate_ichimoku(data, 1)
    data30m = calculate_ichimoku(data, 0.5)
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
