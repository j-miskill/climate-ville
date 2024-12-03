import dash
from dash import html                        # basic HTML syntax (header, bolds, etc)
from dash import dcc                         # part of dash that has interactive elements
from dash.dependencies import Input, Output  # handling user input and outputing things onto dashboard
import plotly.figure_factory as ff
from climate import ClimateAgent
from census import CensusData
import pandas as pd
import numpy as np
import os


# create the dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# set up contrans and postgres connections
ca = ClimateAgent()
cd = CensusData()
server, engine = cd.connect_to_postgres(os.getenv("POSTGRES_PASSWORD"), host="postgres") # networking docker containers


# create fixed variables for use in the dashboard



cities = list(cd.get_all_cities())

dropdown_options = cities # choose a city to view information on it


# populate the layout with callbacks included

app.layout = html.Div([

html.H1("Understand How Changes in Climate Are Related to Socioeconomic Factors for Virginia", style={'text-align': 'center'}),
html.Div([
    dcc.Markdown("Select your county of Virginia here"),
    dcc.Dropdown(id='dropdown', options=dropdown_options, value='norfolk')
    ], style= {"width":"25%", "float": "left"}),
html.Div([
    dcc.Tabs([
        
        dcc.Tab(label="Climate", children=[
            
            # 
            

            # 
           
            ]),

        dcc.Tab(label="Socioeconomic Factors", children=[]),

        dcc.Tab(label="Analyzes", children=[
            dcc.Graph(id="ideograph")
        ]),
])
], style= {"width":"72%", "float": "right"})
])


"""
    callback methods
"""





# run the dash app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)