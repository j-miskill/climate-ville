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

feature_query = """
SELECT * 
FROM city_data
"""

features = list(pd.read_sql_query(query, con=engine).columns)


# populate the layout with callbacks included

app.layout = html.Div([

html.H1("Understand How Changes in Climate Are Related to Socioeconomic Factors for Virginia", style={'text-align': 'center'}),
html.Div([
    dcc.Markdown("Select two Virginia cities to compare"),
    dcc.Dropdown(id='state1', options=dropdown_options, value='norfolk, virginia'),
    dcc.Dropdown(id='state2', options=dropdown_options, value='augusta, virginia'),
    ], style= {"width":"15%", "float": "left"}),
html.Div([
    dcc.Tabs([
        
        dcc.Tab(label="Climate Data", children=[
            
            # 
            dcc.Markdown(id='state_one_name'),
            dcc.Graph(id="state_one_climate_table"),
            dcc.Markdown(id='state_two_name'),
            dcc.Graph(id="state_two_climate_table"),
            ]),

        dcc.Tab(label="Socioeconomic Data", children=[
            dcc.Markdown(id='econ_state_one_name'),
            dcc.Graph(id="state_one_econ_table"),
            dcc.Markdown(id='econ_state_two_name'),
            dcc.Graph(id="state_two_econ_table"),
        ]),

        dcc.Tab(label="Comparison Graphs", children=[
            dcc.Graph(id="state_one_climate_trends"),
            dcc.Graph(id="state_two_climate_trends"),
            dcc.Markdown("Comparing average prcp, tmax, and tmin values for the two cities"),
            dcc.Graph(id="average_climates")
        ]),
])
], style= {"width":"80%", "float": "right"})
])

"""
    callback methods
"""
@app.callback([Output(component_id="state_one_name", component_property="children")],
              [Input(component_id="state1", component_property="value"),])
def get_id(b):
      return [b]


@app.callback([Output(component_id="state_two_name", component_property="children")],
              [Input(component_id="state2", component_property="value"),])
def get_id(b):
      return [b]


@app.callback([Output(component_id="econ_state_one_name", component_property="children")],
              [Input(component_id="state1", component_property="value"),])
def get_id(b):
      return [b]


@app.callback([Output(component_id="econ_state_two_name", component_property="children")],
              [Input(component_id="state2", component_property="value"),])
def get_id(b):
      return [b]


@app.callback([Output(component_id="state_one_climate_table", component_property="figure")],
              [Input(component_id="state1", component_property="value"),])
def get_climate_table(state1):
    state_one_station_id = ca.get_station_id_from_postgres(state1, engine=engine)
    df = ca.get_climate_data_from_postgres(state_one_station_id, engine=engine).sort_values(by='date')
    return [ff.create_table(df.tail(10))]


@app.callback([Output(component_id="state_two_climate_table", component_property="figure")],
              [Input(component_id="state2", component_property="value"),])
def get_climate_table(state2):
    state_two_station_id = ca.get_station_id_from_postgres(state2, engine=engine)
    df = ca.get_climate_data_from_postgres(state_two_station_id, engine=engine).sort_values(by='date')
    return [ff.create_table(df.tail(10))]

@app.callback([Output(component_id="state_one_econ_table", component_property="figure")],
              [
                Input(component_id="state1", component_property="value"),    
            ])
def get_socioeconomic_table(b):
    b = b.replace(", virginia", "")
    df = cd.query_city_data(b, engine=engine)
    figure = ff.create_table(df.tail(20))
    # Adjust layout to set a fixed height and add scrolling
    figure.update_layout(xaxis=dict(rangeslider=dict(visible=True),
                             type="linear"))
    return [figure]

@app.callback([Output(component_id="state_two_econ_table", component_property="figure")],
              [
                Input(component_id="state2", component_property="value"),    
            ])
def get_socioeconomic_table(b):
    b = b.replace(", virginia", "")
    df = cd.query_city_data(b, engine=engine)
    figure = ff.create_table(df.tail(20))
    # Adjust layout to set a fixed height and add scrolling
    figure.update_layout(xaxis=dict(rangeslider=dict(visible=True),
                             type="linear"))
    return [figure]

@app.callback([Output(component_id="state_one_climate_trends", component_property="figure")],
              [Input(component_id="state1", component_property="value")])
def calculate_climate_trends(b):
    station_id = ca.get_station_id_from_postgres(b, engine=engine)
    fig = ca.plot_temperature_trend(station_id, engine=engine)
    return [fig]

@app.callback([Output(component_id="state_two_climate_trends", component_property="figure")],
              [Input(component_id="state2", component_property="value")])
def calculate_climate_trends(b):
    station_id = ca.get_station_id_from_postgres(b, engine=engine)
    fig = ca.plot_temperature_trend(station_id, engine=engine)
    return [fig]

@app.callback([Output(component_id="average_climates", component_property="figure")],
              [
                   Input(component_id="state1", component_property="value"),
                   Input(component_id="state2", component_property="value")
                   
                   ]
              )
def compare_average_climates(state1, state2):
     
    state_one_station_id = ca.get_station_id_from_postgres(state1, engine=engine)
    state_two_station_id = ca.get_station_id_from_postgres(state2, engine=engine)

    state_one_df = ca.get_climate_data_from_postgres(station_id=state_one_station_id,engine=engine)
    state_two_df = ca.get_climate_data_from_postgres(station_id=state_two_station_id,engine=engine)

    full_df = pd.concat([state_one_df, state_two_df])
    full_df['date'] = pd.to_datetime(full_df['date'])
    full_df['year'] = full_df['date'].dt.year
    full_df['month'] = full_df['date'].dt.month
    agg_df = full_df.groupby(["id", "year"], as_index=False).agg(
        {"prcp": "mean",
        "tmax": "mean",
        "tmin": "mean"}
    )

    return [ff.create_table(agg_df.tail(10))]



def compare_average_socioeconomic_status(state1, state2):
     pass

# run the dash app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)