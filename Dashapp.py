import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from mibian import BS

timeseries = pd.read_csv('australian-us-dollar-exchange-rate-historical-chart.csv')
timeseries.sort_values('date', inplace = True)

volatility_data = pd.read_csv("Option_data_NIFTY.csv")
volatility_data['IV'] = 0
volatility_data['Delta'] =0
volatility_data['Gamma']= 0
volatility_data['Vega'] = 0

for row in range(0,len(volatility_data)):       
    underlyingPrice = volatility_data.iloc[row]['Underlying Value']
    strikePrice = volatility_data.iloc[row]['Strike Price']
    interestRate = 0
    daysToExpiration = volatility_data.iloc[row]['Time to Expiry']
    
    callPrice = volatility_data.iloc[row]['LTP']
    
    result = BS([underlyingPrice, strikePrice, interestRate, daysToExpiration],
                callPrice = callPrice)
    
    volatility_data.iloc[row,volatility_data.columns.get_loc('IV')] = result.impliedVolatility

    volatility = volatility_data.iloc[row]['IV']

    result = BS([underlyingPrice, strikePrice, interestRate, daysToExpiration],
                volatility = volatility)

    volatility_data.iloc[row,volatility_data.columns.get_loc('Delta')] = result.callDelta

    volatility_data.iloc[row, volatility_data.columns.get_loc("Gamma")] = result.gamma

    volatility_data.iloc[row,volatility_data.columns.get_loc("Vega")] = result.vega
    
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]    

app = dash.Dash(__name__, external_stylesheets= external_stylesheets)

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🥑", className="header-emoji"),
                html.H1(
                    children="PRMIA dashboard", className="header-title"
                ),
                html.P(
                    children="Orbitrage",
                    className = "header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                  html.Div(
                    children=[
                        html.Div(children="Date", className="date-picker"),
                        dcc.Dropdown(
                            id="date-picker",
                            options=[
                                {"label": datevalue, "value": datevalue}
                                for datevalue in volatility_data.Date.unique()
                            ],
                            value="10-11-2017",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        figure = {
                            "data":[
                                {
                                    "x": timeseries['date'],
                                    "y": timeseries[' value'],
                                    'type':'lines',
                                },
                            ],
                            "layout":{"title":"Time series of Underlying"},
                        },
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="volatility-smile-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children= dcc.Graph(
                        id = "Delta-chart", config = {"displayModeBar":False},
                    ),
                    className = "card",
                ),
                html.Div(
                    children = dcc.Graph(
                        id = "Gamma-chart",config = {"displayModeBar":False},
                    ),
                    className = "card",
                ),
                html.Div(
                    children = dcc.Graph(
                        id = "Vega-chart", config = {"displayModeBar":False},
                    ),
                    className = "card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    [Output("volatility-smile-chart", "figure"), Output("Delta-chart","figure"), Output("Gamma-chart","figure"), Output("Vega-chart","figure")],
    [
        Input("date-picker", "value"),
    ],
)
def update_charts(datevalue):

    dataframe = pd.DataFrame()
    dataframe['Strike Price'] = volatility_data[volatility_data['Date']==datevalue]['Strike Price']
    dataframe['IV'] = volatility_data[volatility_data['Date']==datevalue]['IV']
    dataframe['Delta'] = volatility_data[volatility_data['Date']==datevalue]['Delta']
    dataframe['Gamma'] = volatility_data[volatility_data['Date']==datevalue]['Gamma']
    dataframe["Vega"] = volatility_data[volatility_data['Date']==datevalue]['Vega']
    dataframe.dropna()

    volatility_smile_chart_figure = {
        "data": [
            {
                "x": dataframe["Strike Price"],
                "y": dataframe["IV"],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {"text": "Volatility Smile", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    Delta_figure = {
        "data": [
            {
                "x": dataframe["Strike Price"],
                "y": dataframe["Delta"],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {"text": "Delta", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    Gamma_figure = {
        "data": [
            {
                "x": dataframe["Strike Price"],
                "y": dataframe["Gamma"],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {"text": "Gamma", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    Vega_figure = {
        "data":[
            {
                "x": dataframe["Strike Price"],
                "y": dataframe["Vega"],
                "type":"lines",
            },
        ],
        "layout": {
            "title": {"text": "Vega", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }

    return volatility_smile_chart_figure, Delta_figure, Gamma_figure, Vega_figure


if __name__ == "__main__":
    app.run_server(debug=True)
