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
stock_options = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'INFY.NS']

#Layout
app.layout = html.Div([
    html.H1("Live Stock Price Dashboard", style={'textAlign': 'center'}),

    dcc.Dropdown(
        id = 'stock-dropdown',
        options=[{'label': stock, 'value': stock} for stock in stock_options],
        value = 'INFY.NS',
        clearable = False
    ),

    dcc.Graph(id='price-graph'),

    dcc.Interval(
        id='interval-component',
        interval=60*1000, #Update every 60 sec
        n_intervals=0
    )

])

#Call Back to update graph
@app.callback(
    Output('price-graph','figure'),
    [Input('stock-dropdown','value'),
    Input('interval-component', 'n_intervals')]
)

def update_graph(selected_stock, n):
    data = yf.download(
        tickers=selected_stock,
        start= "2025-01-01",
        end="2025-04-19",
        interval="1d",
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

    print(data.tail(10))  # Debug check
    print(data[['Close']].tail())  # Sanity check
    print(type(data.index[0]))
    print(data.columns)

    # Plot
    fig = go.Figure()
    # fig.add_trace(go.Scatter(
    #     x=data.index,
    #     y=data['Close'],
    #     mode='candlestick+markers',
    #     name=selected_stock
    # ))


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
        xaxis_rangeslider_visible=True,
        template = 'plotly_dark'
    #     xaxis=dict(
    #         tickformat='%b %d %H:%M',
    #         tickangle=-45,
    #         showgrid=True
    #     ),
    #     yaxis=dict(showgrid=True),
    #     margin=dict(l=40, r=40, t=40, b=80)
    )

    return fig


#Run app
if __name__ == '__main__':
    app.run(debug=True)
