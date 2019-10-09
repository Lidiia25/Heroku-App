import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd


def get_url(**kwargs):
    url = 'https://data.cityofnewyork.us/resource/nwxe-4ae8.json?'
    params = []
    for k, v in kwargs.items():
        if type(v) == list:
            v = '&'.join(v)
        params.append('$' + k + '=' + v)
    return (url + '&'.join(params)).replace(' ', '%20')


app = dash.Dash()

species_url = get_url(select='spc_common', group='spc_common', order='spc_common')
species = pd.read_json(species_url)

species_list = list(species['spc_common'])

boro_list = ['Bronx', 'Brooklyn', 'Manhattan', 'Queens', 'Staten Island']

app.layout = html.Div([
    html.Div([

        html.H3('New York Tree Health by Stewardship'),

        html.Div([
            dcc.RadioItems(
                id='boro_choice',
                options=[{'label': i, 'value': i} for i in boro_list],
                value='Bronx'
            )

        ], style={'width': '30%', 'float': 'center'}),

        html.Div([
            dcc.Dropdown(
                id='species_choice',
                options=[{'label': i, 'value': i} for i in species_list],
                value='American beech'
            )
        ], style={'width': '20%', 'float': 'center'})

    ]),

    html.Div([

        html.Div([
            dcc.Graph(id='num_graph')
        ],
            style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='prop_graph')
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

], style={'padding': 20, 'font-family': 'Arial'})


@app.callback(
    Output('num_graph', 'figure'),
    [Input('boro_choice', 'value'),
     Input('species_choice', 'value')])
def update_graph(boro_choice, species_choice):
    url = get_url(select='health,steward,count(tree_id)',
                  where=[
                      "spc_common='" + species_choice + "'",
                      "boroname='" + boro_choice + "'"
                  ],
                  group='spc_common,health,steward',
                  order='spc_common,steward,health')
    trees = pd.read_json(url)

    trees.loc[trees['steward'] == 'None', 'steward'] = '0-None'

    trees[['steward', 'health']] = trees[['steward', 'health']].astype('category')
    steward_cats = list(trees['steward'].unique())
    steward_cats.sort()
    trees['steward'] = trees['steward'].cat.reorder_categories(steward_cats)
    h_cats = ['Good', 'Fair', 'Poor']
    health_cats = sorted(list(trees['health'].unique()), key=lambda x: h_cats.index(x))
    trees['health'] = trees['health'].cat.reorder_categories(health_cats)

    traces = []
    colors = ['#588c7e ', '#f2e394', '#d96459']
    i = 0
    for h in trees.health.cat.categories.tolist():
        trees_by_health = trees[trees['health'] == h]
        traces.append(go.Bar(
            x=trees_by_health['steward'],
            y=trees_by_health['count_tree_id'],
            marker=dict(color=colors[i]),
            name=h
        ))
        i += 1

    return {
        'data': traces,
        'layout': go.Layout(
            title='Number of Trees by Health and Stewardship',
            barmode='stack',
            xaxis={
                'title': 'Steward Activity'
            },
            yaxis={
                'title': 'Number of Trees in Good, Fair and Poor Health'
            }
        )
    }


@app.callback(
    Output('prop_graph', 'figure'),
    [Input('boro_choice', 'value'),
     Input('species_choice', 'value')])
def update_graph(boro_choice, species_choice):
    ###duplicate code..

    url = get_url(select='health,steward,count(tree_id)',
                  where=[
                      "spc_common='" + species_choice + "'",
                      "boroname='" + boro_choice + "'"
                  ],
                  group='spc_common,health,steward',
                  order='spc_common,steward,health')

    trees = pd.read_json(url)

    trees.loc[trees['steward'] == 'None', 'steward'] = '0-None'

    trees[['steward', 'health']] = trees[['steward', 'health']].astype('category')
    steward_cats = list(trees['steward'].unique())
    steward_cats.sort()
    trees['steward'] = trees['steward'].cat.reorder_categories(steward_cats)
    h_cats = ['Good', 'Fair', 'Poor']
    health_cats = sorted(list(trees['health'].unique()), key=lambda x: h_cats.index(x))
    trees['health'] = trees['health'].cat.reorder_categories(health_cats)

    props = trees.groupby(['steward', 'health']).agg({'count_tree_id': 'sum'}).groupby(level=0).apply(
        lambda g: g / g.sum()).reset_index()

    traces = []
    colors = ['#588c7e ', '#f2e394', '#d96459']
    i = 0
    for h in props.health.cat.categories.tolist():
        props_by_health = props[props['health'] == h]
        traces.append(go.Bar(
            x=props_by_health['steward'],
            y=props_by_health['count_tree_id'],
            marker=dict(color=colors[i]),
            name=h
        ))
        i += 1

    return {
        'data': traces,
        'layout': go.Layout(
            title='Proportion of Trees by Health and Stewardship:',
            # title='Proportion of Trees by Health and Stewardship',
            barmode='stack',
            xaxis={
                'title': 'Steward Activity'
            },
            yaxis={
                'title': 'Proportion of Trees in Good, Fair and Poor Health'
            }
        )
    }


# app.css.config.serve_locally = False

# app.css.append_css({
#   'external_url': 'https://codepen.io/chriddyp/pen/dZVMbK.css'})

if __name__ == '__main__':
    app.run_server()
