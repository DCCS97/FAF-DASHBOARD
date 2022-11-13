import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import requests
import json
import collections
import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import numpy as np

load_figure_template("quartz")


app = Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ, dbc.icons.FONT_AWESOME])

server=app.server

app.layout = dbc.Container([

dbc.Row([
    dbc.Col([
    html.H1("FAF DASHBOARD")
    ], width=8)
    ], justify="center"),



dbc.Row([
    dbc.Col([
    html.Div([
            html.Div(children='''
                Enter FAF Name:
            '''),
            dcc.Input(id='input', value='', type='text',debounce=True),

            ])
    ],width=4),
    dbc.Col([
            html.Div(
                    [html.H6("Global Rating"), html.H6(id='current-global-rating') ],
                    className='opacity-100 p-2 m-1 text-light fw-bold rounded border border-secondary')],width=2),
    dbc.Col([
            html.Div(
                    [html.H6("Past FAF Names"), html.H6(id='name-history')],
                    className='opacity-100 p-2 m-1 text-light fw-bold rounded border border-secondary')],width=3)


    ]),

dbc.Row([
    dbc.Col([
            html.Div(id='faction-frequency', className="border m-1")
            ],width=4),
    dbc.Col([
            html.Div(id='global-rating-over-time', className="border m-1")
            ],width=8)

        ]),
dbc.Row([
    dbc.Col([
            html.Div(id='rating-change-scatter', className="border m-1")
            ],width=8),
    dbc.Col([
            html.Div(id='win-loss', className="border m-1")
            ],width=4)

        ]),



])
@app.callback(
    Output(component_id='global-rating-over-time', component_property='children'),
    Output(component_id='faction-frequency', component_property='children'),
    Output(component_id='current-global-rating', component_property='children'),
    Output(component_id='name-history', component_property='children'),
    Output(component_id='win-loss', component_property='children'),
    Output(component_id='rating-change-scatter', component_property='children'),
    [Input(component_id='input', component_property='value')]
)
def update_value(input_login):
    datapy = api_call(input_login)
    global_rating_list=[]
    for data in datapy['data']:
        if type(data['attributes']['scoreTime'])==str:
            if type(data['attributes']['afterMean'])==float:
                afterMean=(data['attributes']['afterMean'])
                afterDeviation=(data['attributes']['afterDeviation'])
                global_rating=round(afterMean-3*afterDeviation)
                global_rating_list.append(global_rating)
    current_global_rating=global_rating_list[0]



    win_loss_list=[]
    for i, j in enumerate(global_rating_list[:-1]):
        if j > global_rating_list[i+1]:
            result_w="Win"
            win_loss_list.append(result_w)
        elif j < global_rating_list[i+1]:
            result_l="Loss"
            win_loss_list.append(result_l)
        else:
            result_na="N/A"
            win_loss_list.append(result_na)




    matchdateslist=[]
    for data in datapy['data']:
        if type(data['attributes']['afterMean'])==float:
            if type(data['attributes']['scoreTime'])==str:
                scoretime=(data['attributes']['scoreTime'])
                matchdateslist.append(scoretime)




    playerfactionlist=[]
    for data in datapy['data']:
        if (data['attributes']['faction']) == 1:
            playerfaction=("UEF")
            playerfactionlist.append(playerfaction)
        elif (data['attributes']['faction']) == 2:
            playerfaction=("Aeon")
            playerfactionlist.append(playerfaction)
        elif (data['attributes']['faction']) == 3:
            playerfaction=("Cybran")
            playerfactionlist.append(playerfaction)
        elif (data['attributes']['faction']) == 4:
            playerfaction=("Seraphim")
            playerfactionlist.append(playerfaction)
        elif (data['attributes']['faction']) == 5:
            playerfaction=("Nomads")
            playerfactionlist.append(playerfaction)
        else:
            playerfaction=("Other")
            playerfactionlist.append(playerfaction)

    for data in datapy['included']:
        player_id=(data['id'])

    name_history=[]
    datapyn=api_call_name(player_id)
    for data in datapyn['data']:
        player_name=(data['attributes']['name'])
        name_history.append(player_name)


    name_history_dropdown = html.Ul([html.Li(x) for x in name_history])



    win_loss_frequency=collections.Counter(win_loss_list)
    df_win_loss_frequency=pd.DataFrame.from_dict(win_loss_frequency, orient ='index').reset_index()
    df_win_loss_frequency.rename(columns={'index': 'Result', 0: 'No. of Games'}, inplace=True)

    rating_change=[]
    for i,j in enumerate(global_rating_list[:10]):
        change=j - global_rating_list[i+1]
        rating_change.append(change)


    df_rating_change=pd.DataFrame({
                                'Rating Change': rating_change,
                                'Date':matchdateslist[0:10],})
    df_rating_change["Color"] = np.where(df_rating_change['Rating Change']<0 , 'red','green')
    df_rating_change["Size"] = 15




    factionfrequency=collections.Counter(playerfactionlist)
    df_faction_frequency=pd.DataFrame.from_dict(factionfrequency, orient ='index').reset_index()
    df_faction_frequency.rename(columns={'index': 'Faction', 0: 'Games Played'}, inplace=True)

    figure = dcc.Graph(id='pie-graph',className="shadow-lg",
    figure=px.line(x=matchdateslist, y=global_rating_list, title="Global Rating Over Time", labels=dict(x="Date",y="Global Rating")))


    figure1 = dcc.Graph(id='pie-graph2', className="shadow-lg",
    figure=px.pie(df_faction_frequency,values="Games Played",names="Faction", hole=.4, title="Faction Played Frequency",
    color="Faction" , color_discrete_map= {'UEF':'#2c9fc8',
                        'Aeon': '#68ab4d',
                        'Cybran':'#dd0001',
                        'Seraphim':'#f9bb2c',
                        'Nomads':'orange'
                          }))


    figure2 = dcc.Graph(id='pie-graph3',className="shadow-lg",
    figure=px.pie(df_win_loss_frequency,values="No. of Games",names="Result",hole=.4, title="Win/Loss Percentage",
        color="Result" , color_discrete_map= {'Win':'#9EE09E',
                            'Loss': '#FF6663',
                              }))



    figure3 = dcc.Graph(id='scatter-chart',className="shadow-lg",
    figure= px.scatter(df_rating_change, x="Date", y="Rating Change", color="Rating Change",title="Rating Change Past 10 Games",
                 size="Size", hover_data=["Rating Change","Date"]))


    return figure, figure1, current_global_rating, name_history_dropdown, figure2, figure3






def api_call(input_login):
    login=input_login
    url = f'https://api.faforever.com/data/gamePlayerStats?include=player&sort=-scoreTime&filter=player.login=={login}&page[limit]=10000'
    r = requests.get(url)
    datapy = json.loads(r.text)

    return datapy

def api_call_name(input_playerid):
    player_id=input_playerid
    url=f'https://api.faforever.com/data/player/{player_id}/names'
    r = requests.get(url)
    datapyn= json.loads(r.text)

    return datapyn





if __name__ == '__main__':
    app.run_server(debug=False)
