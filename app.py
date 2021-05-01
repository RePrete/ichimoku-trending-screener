import configparser

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from dash import dash
from dash.dependencies import Input, Output, State
from flask_caching import Cache

import config

configparser.ConfigParser()

TIMEOUT = 60
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
cache = Cache(app.server, config={
    'CACHE_TYPE': 'RedisCache',
    'CACHE_KEY_PREFIX': 'its_',
    'CACHE_REDIS_URL': config.REDIS_URL,
})
# Major pairs
major_pairs = [
    {'label': 'EUR/USD', 'value': 'EURUSD=X'},
    {'label': 'USD/JPY', 'value': 'USDJPY=X'},
    {'label': 'GBP/USD', 'value': 'GBPUSD=X'},
    {'label': 'USD/CHF', 'value': 'USDCHF=X'},
    {'label': 'AUD/USD', 'value': 'AUDUSD=X'},
    {'label': 'USD/CAD', 'value': 'USDCAD=X'},
    {'label': 'NZD/USD', 'value': 'NZDUSD=X'},
    {'label': 'Gold', 'value': 'GC=F'},
    {'label': 'Silver', 'value': 'SI=F'},
]
other_pairs = [
    # Other pairs
    # Eur pairs
    {'label': 'EUR/GBP', 'value': 'EURGBP=X'},
    {'label': 'EUR/AUD', 'value': 'EURAUD=X'},
    {'label': 'EUR/NZD', 'value': 'EURNZD=X'},
    {'label': 'EUR/CAD', 'value': 'EURCAD=X'},
    {'label': 'EUR/CHF', 'value': 'EURCHF=X'},
    {'label': 'EUR/JPY', 'value': 'EURJPY=X'},
    # Gbp pairs
    {'label': 'GBP/JPY', 'value': 'GBPJPY=X'},
    {'label': 'GBP/AUD', 'value': 'GBPAUD=X'},
    {'label': 'GBP/NZD', 'value': 'GBPNZD=X'},
    {'label': 'GBP/CAD', 'value': 'GBPCAD=X'},
    {'label': 'GBP/CHF', 'value': 'GBPCHF=X'},
    # Aud pairs
    {'label': 'AUD/JPY', 'value': 'AUDJPY=X'},
    {'label': 'AUD/NZD', 'value': 'AUDNZD=X'},
    {'label': 'AUD/CAD', 'value': 'AUDCAD=X'},
    {'label': 'AUD/CHF', 'value': 'AUDCHF=X'},
    # Nzd pairs
    {'label': 'NZD/JPY', 'value': 'NZDJPY=X'},
    {'label': 'NZD/CAD', 'value': 'NZDCAD=X'},
    {'label': 'NZD/CHF', 'value': 'NZDCHF=X'},
    # Cad pairs
    {'label': 'CAD/JPY', 'value': 'CADJPY=X'},
    {'label': 'CAD/CHF', 'value': 'CADCHF=X'},
    # Chf pairs
    {'label': 'CHF/JPY', 'value': 'CHFJPY=X'},
]
all_pairs = major_pairs + other_pairs


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
    p_bl = (data.tail(bl_coef + 1).head(bl_coef)['High'].max() + data.tail(bl_coef + 1).head(bl_coef)['Low'].min()) / 2
    p_ssa = (p_cl + p_bl) / 2
    p_ssb = (data.tail(ssb_coef + 1).head(ssb_coef)['High'].max() + data.tail(ssb_coef + 1).head(ssb_coef)[
        'Low'].min()) / 2

    if c_bl > p_bl and c_bl > c_ssb:
        if c_ssb > p_ssb or (c_ssb == p_ssb and c_ssa > p_ssa):
            return 1
    elif c_bl < p_bl and c_bl < c_ssb:
        if c_ssb < p_ssb or (c_ssb == p_ssb and c_ssa < p_ssa):
            return -1
    return 0


@cache.memoize(timeout=TIMEOUT)
def get_yfinance_data(ticker, period, interval):
    return yf.Ticker(ticker).history(period=period, interval=interval)


@cache.memoize(timeout=3600)
def get_yfinance_h_data(ticker):
    return yf.Ticker(ticker).history(period='52h', interval='1h')


@cache.memoize(timeout=5)
def get_yfinance_m_data(ticker):
    return yf.Ticker(ticker).history(period='16h', interval='5m')


@cache.memoize(timeout=TIMEOUT)
def get_data(ticker):
    data = get_yfinance_h_data(ticker)

    data1d = calculate_ichimoku(data, '1d')
    data4h = calculate_ichimoku(data, '4h')
    data1h = calculate_ichimoku(data, '1h')
    if data1h != 0 and (data1d == data1h or data4h == data1h):
        trending = 1
    else:
        trending = 0

    return {
        'Ticker': [ticker],
        'Daily': [data1d],
        '4h': [data4h],
        '1h': [data1h],
        'Data': [data],
        'Trending': [trending]
    }


def filter_trending(df):
    return df[df['Trending'] == 1]


def update_tickers(tickers_list, only_trending):
    result = pd.concat([
        pd.DataFrame(get_data(ticker)) for ticker in tickers_list],
        ignore_index=True
    ).set_index('Ticker')
    if only_trending:
        return filter_trending(result)
    return result


def update_callback(tickers_list):
    return pd.DataFrame(update_tickers(tickers_list, False))


CONTROLS_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}
controls = dbc.Card(
    style=CONTROLS_STYLE,
    children=[
        dbc.FormGroup([
            html.H4('Major Pairs'),
            dbc.Checklist(
                id="all-or-none-major",
                options=[{"label": "Select All", "value": "all"}],
                value=[],
            ),
            dbc.Checklist(
                id="major-pairs-checklist",
                options=major_pairs,
                value=[i['value'] for i in major_pairs[:5]],
            )
        ]),
        dbc.FormGroup([
            html.H4('Other pairs'),
            dbc.Checklist(
                id="all-or-none-pairs",
                options=[{"label": "Select All", "value": "all"}],
                value=[],
            ),
            dbc.Checklist(
                id="other-pairs-checklist",
                options=other_pairs,
                value=[],
            ),
        ]),
    ]
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                html.Div(
                    id='hidden-div',
                    style={'display': 'none'},
                    children=[
                        dcc.Interval(
                            id='data-interval-component',
                            interval=15 * 60 * 1000,  # in milliseconds
                            n_intervals=0
                        )
                    ]
                ),
                dbc.Col(controls, md=2),
                dbc.Col(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.H4('Timeframe trend'),
                                dcc.Graph(id='trending-chart')
                            ])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H4(id='selected-ticker'),
                                dcc.Graph(id='selected-chart'),
                                dcc.Interval(
                                    id='interval-component',
                                    interval=20 * 1000,  # in milliseconds
                                    n_intervals=0
                                )
                            ])
                        ])
                    ],
                    md=10
                )
            ],
            align="center",
        )
    ],
    fluid=True
)


@app.callback(
    Output("major-pairs-checklist", "value"),
    [Input("all-or-none-major", "value")],
    [State("major-pairs-checklist", "options")],
)
def select_all_none_major(all_selected, options):
    if not all_selected:
        return [major_pairs[0]['value']]

    all_or_none = [option["value"] for option in options]
    return all_or_none


@app.callback(
    Output("other-pairs-checklist", "value"),
    [Input("all-or-none-pairs", "value")],
    [State("other-pairs-checklist", "options")],
)
def select_all_none_other(all_selected, options):
    if not all_selected:
        return []

    all_or_none = [option["value"] for option in options]
    return all_or_none


@app.callback(
    Output("trending-chart", "figure"),
    Input("major-pairs-checklist", "value"),
    Input("other-pairs-checklist", "value"),
    Input("interval-component", "n_intervals")
)
def update_chart(major, other, n_intervals):
    tickers = major + other
    if not tickers:
        return go.Figure()

    # df = update_callback(tickers)
    data = df.iloc[df.index.isin(tickers)]

    # Replace ticker with relative label
    data.reset_index(inplace=True)
    for i, row in data.iterrows():
        data.at[i, 'Ticker'] = pair_value_to_label(row['Ticker'])
    data.set_index('Ticker', inplace=True)

    fig = go.Figure()
    columns = ['Daily', '4h', '1h']
    fig.add_trace(go.Heatmap(
        x=data.index.values,
        y=columns,
        z=data[columns].transpose(),
        zmin=-1, zmax=1,
        colorscale=['#c62828', '#fffde7', '#558b2f'],
        colorbar=dict(
            title="Trend analysis",
            titleside="top",
            tickmode="array",
            tickvals=[-1, 0, 1],
            ticktext=["Downtrend", "Ranging", "Uptrend"],
            ticks="outside"
        )
    ))
    return fig
    # return px.imshow(df[['Daily', '4h', '1h']].transpose(), color_continuous_scale='RdYlGn', zmin=-1, zmax=1)


@app.callback(
    Output("selected-chart", "figure"),
    Output("selected-ticker", "children"),
    Input("trending-chart", "hoverData"),
)
def draw_charts(clicked):
    if clicked is None:
        ticker = major_pairs[0]['value']
    else:
        ticker = pair_label_to_value(clicked['points'][0]['x'])

    df = get_yfinance_m_data(ticker)
    figure = go.Figure(
        data=go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']
        )
    )
    figure.update_layout(xaxis_rangeslider_visible=False)
    label = pair_value_to_label(ticker)
    return figure, label + ' 5 min chart'


def pair_value_to_label(ticker):
    return next(i['label'] for i in all_pairs if i['value'] == ticker)


def pair_label_to_value(ticker):
    return next(i['value'] for i in all_pairs if i['label'] == ticker)


@app.callback(
    Output('hidden-div', 'children'),
    Input('hidden-div', 'children')
)
def update_all_pairs(input):
    df = update_callback(i['value'] for i in all_pairs)


df = update_callback(i['value'] for i in all_pairs)
if __name__ == '__main__':
    app.run_server(debug=True)
