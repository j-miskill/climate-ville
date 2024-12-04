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
import plotly.figure_factory as ff



# create the dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# set up contrans and postgres connections
ca = ClimateAgent()
cd = CensusData()
server, engine = cd.connect_to_postgres(os.getenv("POSTGRES_PASSWORD"), host="postgres") # networking docker containers


# create fixed variables for use in the dashboard

query = """
SELECT *
FROM city_ids
"""
cities = list(pd.read_sql_query(query, con=engine)['city'])
cs = []
for c in cities:
    c = c.replace(", virginia", "")
    cs.append(c)
dropdown_options = cities # choose a city to view information on it


# populate the layout with callbacks included

app.layout = html.Div([

html.H1("Understand How Changes in Climate Are Related to Socioeconomic Factors for Virginia", style={'text-align': 'center'}),
html.Div([
    dcc.Markdown("Select your county of Virginia here"),
    dcc.Dropdown(id='dropdown', options=dropdown_options, value='norfolk, virginia')
    ], style= {"width":"25%", "float": "left"}),
html.Div([
    dcc.Tabs([
        
        dcc.Tab(label="Climate", children=[
            
            # 
            dcc.Graph(id="climate_table"),
            

            # 
           
            ]),

        dcc.Tab(label="Socioeconomic Factors", children=[
            dcc.Graph(id="socioeconomic_table"),
        ]),

        dcc.Tab(label="Analyzes", children=[
            dcc.Graph(id="climate_trends")
        ]),
])
], style= {"width":"72%", "float": "right"})
])


"""
    callback methods
"""
@app.callback([Output(component_id="climate_table", component_property="figure")],
              [Input(component_id="dropdown", component_property="value")])
def get_climate_table(b):
    station_id = ca.get_station_id_from_postgres(b, engine=engine)
    df = ca.get_climate_data_from_postgres(station_id, engine=engine)
    return [ff.create_table(df.head(20))]

@app.callback([Output(component_id="socioeconomic_table", component_property="figure")],
              [Input(component_id="dropdown", component_property="value")])
def get_socioeconomic_table(b):
    b = b.replace(", virginia", "")
    df = cd.query_city_data(b, engine=engine)
    figure = ff.create_table(df.head(20))
    # Adjust layout to set a fixed height and add scrolling
    figure.update_layout(xaxis=dict(rangeslider=dict(visible=True),
                             type="linear"))
    return [figure]

@app.callback([Output(component_id="climate_trends", component_property="figure")],
              [Input(component_id="dropdown", component_property="value")])
def calculate_climate_trends(b):
    # b = b.replace(", virginia", "")
    # print(b)
    station_id = ca.get_station_id_from_postgres(b, engine=engine)
    fig = ca.plot_temperature_trend(station_id, engine=engine)
    return [fig]

# run the dash app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)