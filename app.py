import dash
from dash import html, dcc
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

# Create a Dash app
app = dash.Dash(__name__)
app.title = "Stock Price Dashboard"

#List of Stock Options
stock_options = ['BAJAJFINSV.NS', 'COALINDIA.NS', 'TVSMOTOR.NS', 'VBL.NS', 'SOLARINDS.NS', 'INFY.NS']

#Layout
app.layout = html.Div([
    html.H1("Live Stock Price Dashboard", style={
        'textAlign': 'center',
        'color': '#1a1a1a',
        'fontFamily': 'Segoe UI, sans-serif',
        'padding': '20px 0',
        'marginBottom' :'10px',
        'fontWeight': 'bold'
    }),

    html.Div
        ([
        dcc.Dropdown(
        id = 'stock-dropdown',
        options=[{'label': stock, 'value': stock} for stock in stock_options],
        value = 'COALINDIA.NS',
        clearable = False,
            style={
                'width': '100%',
                'fontSize': '16px',
                'fontFamily': 'Segoe UI',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}
        ),

    dcc.Dropdown (
        id ='period-dropdown',
        options=[
            {'label' : '1 Day', 'value' : '1d'},
            {'label' : '7 Days', 'value' : '7d'},
            {'label' : '1 Month', 'value' : '1mo'},
            {'label' : '3 Months', 'value' : '3mo'},
            {'label' : '6 Months', 'value' : '6mo'},
            {'label' : '1 Year', 'value' : '1y'},
        ],
        value ='7d',
        clearable=False,
        style={
            'width': '100%',
            'fontSize': '16px',
            'fontFamily': 'Segoe UI',
            'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}
        ),

    dcc.Dropdown(
        id='interval-dropdown',
        options=[
            {'label': '1 minutes', 'value': '1m'},
            {'label': '5 minutes', 'value': '5m'},
            {'label': '15 minutes', 'value': '15m'},
            {'label': '30 minutes', 'value': '30m'},
            {'label': '1 Hour', 'value': '60m'},
            {'label': '1 Day', 'value': '1d'}
        ],
        value='1d',
        clearable=False,
        style={
            'width': '100%',
            'fontSize': '16px',
            'fontFamily': 'Segoe UI',
            'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}
        ),
    ], style = {
        'display': 'flex',
        'justifyContent': 'center',
        'gap': '15px',
        'marginBottom': '20px',
        'width': '100%',
        'maxWidth': '1100px',
        'margin': '0 auto'}
    ),

    dcc.Graph(id='price-graph',
              style=
              {
                  'height': '700px','borderRadius': '12px',
                  'overflow': 'hidden',
                  'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.06)'}
              ),

    dcc.Interval(
        id='interval-component',
        interval=60 * 1000, #Update every 60 sec
        n_intervals=0
    )

], style={
    'backgroundColor': '#ffffff',
    'padding': '20px',
    'borderRadius': '12px',
    'boxShadow': '0 4px 12px rgba(0,0,0,0.05)',
    'marginBottom': '30px'
    }

)

#Call Back to update graph
@app.callback(
    Output('price-graph','figure'),
    [
        Input('stock-dropdown', 'value'),
        Input('period-dropdown', 'value'),
        Input('interval-dropdown', 'value'),
        Input('interval-component', 'n_intervals')
    ]
)

def update_graph(selected_stock,selected_period, selected_interval, n):
    data = yf.download(
        tickers=selected_stock,
        period= selected_period,
        interval= selected_interval,
        start= "2025-01-01",
        end="2025-04-19",
        group_by="ticker",
        progress=False
    )

    # Flatten if multi-indexed
    if isinstance(data.columns, pd.MultiIndex):
        data = data[selected_stock]  # Get only that stock's columns


    if data.empty or 'Close' not in data:
        fig = go.Figure()
        fig.update_layout(
            title="No Data Available",
            xaxis_title="Time",
            yaxis_title="Price"
        )
        return fig

    # Ensure correct datetime index and drop NaNs
    data.index = pd.to_datetime(data.index).tz_localize(None)
    data = data.sort_index()
    data = data[data['Close'].notna()]
    # data = data.tail(60)

    print(data.tail(10))  # Debug check
    print(data[['Close']].tail())  # Sanity check
    print(type(data.index[0]))
    print(data.columns)

    # Plot
    fig = go.Figure()


    fig.add_trace(go.Candlestick(
        x = data.index,
        open = data['Open'],
        high = data['High'],
        low = data['Low'],
        close = data['Close'],
        increasing_line_color = 'green',
        decreasing_line_color = 'red'

    ))

    fig.update_layout(
        title=f'{selected_stock} Candle Stick Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        font = dict(
            size=11,
            family='Segoe UI, sans-serif',
            color = '#333333'
        ),
        xaxis_rangeslider_visible=True,
        template = 'ggplot2',
        height = 480,
        # plot_bgcolor='#f5f5f7',  # 👈 matches outer div
        paper_bgcolor='#f5f5f7',
        xaxis = dict(
            nticks = 10,
            tickformat='%b %d',
            tickangle=-30,
            showspikes =True,
        ),
        yaxis=dict(showgrid=True),
        margin=dict(l=40, r=40, t=40, b=60),
    hovermode = 'x unified'
    )


    return fig


#Run app
if __name__ == '__main__':
    app.run(debug=True)
