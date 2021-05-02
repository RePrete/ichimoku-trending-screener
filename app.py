import configparser

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash
from dash.dependencies import Input, Output, State
from flask_caching import Cache

import config
import currency_strength
import finance_data
from finance_data import get_data, get_yfinance_m_data

configparser.ConfigParser()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

cache = Cache(app.server, config={
    'CACHE_TYPE': 'RedisCache',
    'CACHE_KEY_PREFIX': 'its_',
    'CACHE_REDIS_URL': config.REDIS_URL,
})

server = app.server
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


@cache.memoize(timeout=config.BASE_TTL)
def get_data(ticker):
    return finance_data.get_data(ticker)


@cache.memoize(timeout=config.MINUTE_DATA_TTL)
def get_yfinance_m_data(ticker):
    return finance_data.get_yfinance_m_data(ticker)


@cache.memoize(timeout=config.BASE_TTL)
def get_yfinance_data(ticker, period, interval):
    return finance_data.get_yfinance_data(ticker, period, interval)


@cache.memoize(timeout=config.HOURLY_DATA_TTL)
def get_yfinance_h_data(ticker):
    return finance_data.get_yfinance_h_data(ticker)


@cache.memoize(timeout=config.BASE_TTL)
def get_currency_strength():
    return currency_strength.calulate()


def update_tickers(tickers_list):
    result = pd.concat([
        pd.DataFrame(get_data(ticker)) for ticker in tickers_list],
        ignore_index=True
    ).set_index('Ticker')
    return result


def update_callback(tickers_list):
    return pd.DataFrame(update_tickers(tickers_list))


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
                            ]),
                            dbc.Col([
                                html.H4("Currency strength"),
                                dcc.Graph(id='currency-strength-chart'),
                                dcc.Interval(
                                    id='currency-strength-interval-component',
                                    interval=5 * 1000,  # in milliseconds
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
    Output("currency-strength-chart", "figure"),
    Input("currency-strength-interval-component", "n_intervals")
)
def update_currency_strength_chart(n_interval):
    df = get_currency_strength()
    return go.Figure(px.bar(df.transpose().sort_values(by=[0], ascending=False)))


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
    data = hourly_data_frame.iloc[hourly_data_frame.index.isin(tickers)]

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


@app.callback(
    Output("selected-chart", "figure"),
    Output("selected-ticker", "children"),
    Input("trending-chart", "hoverData"),
    Input("trending-chart", "clickData"),
)
def draw_charts(hover, clicked):
    if hover is not None:
        ticker = pair_label_to_value(hover['points'][0]['x'])
    elif clicked is not None:
        ticker = pair_label_to_value(clicked['points'][0]['x'])
    else:
        ticker = major_pairs[0]['value']

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
    hourly_data_frame = update_callback(i['value'] for i in all_pairs)


hourly_data_frame = update_callback(i['value'] for i in all_pairs)
if __name__ == '__main__':
    app.run_server(debug=True)
