import pandas as pd
from numpy import log
import yfinance as yf
from yfinance import shared

pairs = [
    'USDCAD=X',
    'USDCHF=X',
    'USDJPY=X',
    'AUDUSD=X',
    'EURUSD=X',
    'GBPUSD=X',
    'NZDUSD=X',
]


def get_val(v1, v2):
    if v2 == 0:
        return
    return log(v1 / v2) * 10000


def get_val_m(v1, v2, v3, v4):
    v1 = v1 * v3
    v2 = v2 * v4
    if v2 == 0:
        return
    return log(v1 / v2) * 10000


def get_val_d(v1, v2, v3, v4):
    if v3 == 0 or v4 == 0:
        return

    v1 = v1 / v3
    v2 = v2 / v4
    if v2 == 0:
        return
    return log(v1 / v2) * 10000


# v1 is the current price, v2 is the price of the starting point
def calulate():
    df = yf.download(' '.join(pairs), period='15', interval='5m', group_by='ticker').tail(2)
    if shared._ERRORS != {}:
        shared._ERRORS = {}
        return pd.DataFrame({
                'eur': [0],
                'usd': [0],
                'jpy': [0],
                'chf': [0],
                'gbp': [0],
                'aud': [0],
                'cad': [0],
                'nzd': [0],
            })

    eurusd = get_val(df['EURUSD=X']['Close'][1], df['EURUSD=X']['Close'][0])
    usdjpy = get_val(df['USDJPY=X']['Close'][1], df['USDJPY=X']['Close'][0])
    usdchf = get_val(df['USDCHF=X']['Close'][1], df['USDCHF=X']['Close'][0])
    gbpusd = get_val(df['GBPUSD=X']['Close'][1], df['GBPUSD=X']['Close'][0])
    audusd = get_val(df['AUDUSD=X']['Close'][1], df['AUDUSD=X']['Close'][0])
    usdcad = get_val(df['USDCAD=X']['Close'][1], df['USDCAD=X']['Close'][0])
    nzdusd = get_val(df['NZDUSD=X']['Close'][1], df['NZDUSD=X']['Close'][0])
    eurjpy = get_val_m(df['EURUSD=X']['Close'][1], df['EURUSD=X']['Close'][0], df['USDJPY=X']['Close'][1], df['USDJPY=X']['Close'][0])
    eurchf = get_val_m(df['EURUSD=X']['Close'][1], df['EURUSD=X']['Close'][0], df['USDCHF=X']['Close'][1], df['USDCHF=X']['Close'][0])
    eurgbp = get_val_d(df['EURUSD=X']['Close'][1], df['EURUSD=X']['Close'][0], df['GBPUSD=X']['Close'][1], df['GBPUSD=X']['Close'][0])
    chfjpy = get_val_d(df['USDJPY=X']['Close'][1], df['USDJPY=X']['Close'][0], df['USDCHF=X']['Close'][1], df['USDCHF=X']['Close'][0])
    gbpchf = get_val_m(df['GBPUSD=X']['Close'][1], df['GBPUSD=X']['Close'][0], df['USDCHF=X']['Close'][1], df['USDCHF=X']['Close'][0])
    gbpjpy = get_val_m(df['GBPUSD=X']['Close'][1], df['GBPUSD=X']['Close'][0], df['USDJPY=X']['Close'][1], df['USDJPY=X']['Close'][0])
    audchf = get_val_m(df['AUDUSD=X']['Close'][1], df['AUDUSD=X']['Close'][0], df['USDCHF=X']['Close'][1], df['USDCHF=X']['Close'][0])
    audjpy = get_val_m(df['AUDUSD=X']['Close'][1], df['AUDUSD=X']['Close'][0], df['USDJPY=X']['Close'][1], df['USDJPY=X']['Close'][0])
    audcad = get_val_m(df['AUDUSD=X']['Close'][1], df['AUDUSD=X']['Close'][0], df['USDCAD=X']['Close'][1], df['USDCAD=X']['Close'][0])
    eurcad = get_val_m(df['EURUSD=X']['Close'][1], df['EURUSD=X']['Close'][0], df['USDCAD=X']['Close'][1], df['USDCAD=X']['Close'][0])
    gbpcad = get_val_m(df['GBPUSD=X']['Close'][1], df['GBPUSD=X']['Close'][0], df['USDCAD=X']['Close'][1], df['USDCAD=X']['Close'][0])
    gbpaud = get_val_d(df['GBPUSD=X']['Close'][1], df['GBPUSD=X']['Close'][0], df['AUDUSD=X']['Close'][1], df['AUDUSD=X']['Close'][0])
    euraud = get_val_d(df['EURUSD=X']['Close'][1], df['EURUSD=X']['Close'][0], df['AUDUSD=X']['Close'][1], df['AUDUSD=X']['Close'][0])
    cadchf = get_val_d(df['USDCHF=X']['Close'][1], df['USDCHF=X']['Close'][0], df['USDCAD=X']['Close'][1], df['USDCAD=X']['Close'][0])
    cadjpy = get_val_d(df['USDJPY=X']['Close'][1], df['USDJPY=X']['Close'][0], df['USDCAD=X']['Close'][1], df['USDCAD=X']['Close'][0])
    audnzd = get_val_d(df['AUDUSD=X']['Close'][1], df['AUDUSD=X']['Close'][0], df['NZDUSD=X']['Close'][1], df['NZDUSD=X']['Close'][0])
    eurnzd = get_val_d(df['EURUSD=X']['Close'][1], df['EURUSD=X']['Close'][0], df['NZDUSD=X']['Close'][1], df['NZDUSD=X']['Close'][0])
    gbpnzd = get_val_d(df['GBPUSD=X']['Close'][1], df['GBPUSD=X']['Close'][0], df['NZDUSD=X']['Close'][1], df['NZDUSD=X']['Close'][0])
    nzdcad = get_val_m(df['NZDUSD=X']['Close'][1], df['NZDUSD=X']['Close'][0], df['USDCAD=X']['Close'][1], df['USDCAD=X']['Close'][0])
    nzdchf = get_val_m(df['NZDUSD=X']['Close'][1], df['NZDUSD=X']['Close'][0], df['USDCHF=X']['Close'][1], df['USDCHF=X']['Close'][0])
    nzdjpy = get_val_m(df['NZDUSD=X']['Close'][1], df['NZDUSD=X']['Close'][0], df['USDJPY=X']['Close'][1], df['USDJPY=X']['Close'][0])

    # Calculate the value of each currency
    pairs_count = 7
    return pd.DataFrame({
        'eur': [(eurusd + eurjpy + eurchf + eurgbp + euraud + eurcad + eurnzd) / pairs_count],
        'usd': [(-eurusd + usdjpy + usdchf - gbpusd - audusd + usdcad - nzdusd) / pairs_count],
        'jpy': [(-eurjpy - usdjpy - chfjpy - gbpjpy - audjpy - cadjpy - nzdjpy) / pairs_count],
        'chf': [(-eurchf - usdchf + chfjpy - gbpchf - audchf - cadchf - nzdchf) / pairs_count],
        'gbp': [(-eurgbp + gbpusd + gbpchf + gbpjpy + gbpaud + gbpcad + gbpnzd) / pairs_count],
        'aud': [(-euraud + audusd + audjpy + audchf - gbpaud + audcad + audnzd) / pairs_count],
        'cad': [(-eurcad - usdcad + cadjpy + cadchf - gbpcad - audcad - nzdcad) / pairs_count],
        'nzd': [(-eurnzd + nzdusd + nzdjpy + nzdchf - gbpnzd + nzdcad - audnzd) / pairs_count],
    })
