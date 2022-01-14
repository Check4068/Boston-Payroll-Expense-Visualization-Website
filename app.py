"""
Dashboard
"""

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
#import plotly.figure_factory as ff


stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

### pandas dataframe to html table

app = dash.Dash(__name__, external_stylesheets=stylesheet)


#Data Preprocessing
Pay2020=pd.read_csv('Payroll2020.csv',header=0)

fname = "US.txt"

with open(fname) as fin:
    data_str = fin.read()

data_list = []
for line in data_str.split('\n'):
    mylist = line.split('\t')
    if len(mylist) > 11:
        data_list.append(mylist)


geo=pd.DataFrame(data_list, columns=['Country', 'POSTAL','City','State','StateCode','county','x2','x3','x4','longitude','latitude','number'])
Pay2020=Pay2020.rename(columns={"DEPARTMENT_NAME": "Department", "QUINN / EDUCATION INCENTIVE": "Education Incentive", "TITLE": "Title", "REGULAR": "Regular", "OTHER":"Other", "OVERTIME": "Overtime", "INJURED": "Injured", "DETAIL": "Detail", "TOTAL EARNINGS": "Total.Earnings" })
Pay2020=Pay2020.loc[Pay2020['POSTAL'].isnull()!=True]
#去掉data

Pay2020new= Pay2020[['Department','Total.Earnings','POSTAL']]

#加上lambda
#Pay2020.loc[Pay2020['Postal']].zfill(5)

df= pd.merge(Pay2020new,geo, on='POSTAL',how='inner')
#df=df.loc[Pay2020county['county'].isnull()!=True]
df= df[df["StateCode"]=="MA"]
df['Total.Earnings']=df['Total.Earnings'].str.replace('$','').str.replace(' ','').str.replace(',','').str.replace(')','').str.replace('(','').astype('float')
df=df.groupby(['county','Department'],as_index=False)['Total.Earnings'].agg({'Total.Earnings':'sum'}).sort_values(by='Total.Earnings',ascending=False)
#.rank(method='first',ascending=False)
#df=df.loc[df['Rank']<50]
df['Rank']=df.groupby('county')['Total.Earnings'].rank(method='first',ascending=False)
df=df.loc[df['Rank']<=10]

df_map= pd.merge(Pay2020new,geo, on='POSTAL',how='inner')
df_map['Total.Earnings']=df_map['Total.Earnings'].str.replace('$','').str.replace(' ','').str.replace(',','').str.replace(')','').str.replace('(','').astype('float')
df_map= df_map[df_map["StateCode"]=="MA"]
df_map=df_map.groupby(['county','POSTAL'],as_index=False)['Total.Earnings'].agg({'Total.Earnings':'sum'}).sort_values(by='Total.Earnings',ascending=False)
df_map

def generate_table(df, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in df.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(min(len(df), max_rows))
        ])
    ])

app = dash.Dash(__name__, external_stylesheets=stylesheet)
#
fig = px.bar(df, x="Department", y="Total.Earnings", color="county")
fig2 = px.pie(df_map,names='county',values='Total.Earnings')


app.layout = html.Div([
    html.H1('City of Boston Payroll 2020',
            style={'textAlign': 'center'}),
    html.H6('Yifu Liu',
            style={'textAlign': 'center'}),
    html.A('Click here for data source',
           href='https://data.boston.gov/dataset/employee-earnings-report',
           target='_blank', style={'textAlign': 'left'}),
    html.P(
        'In this project, users can study the top 10 departments with the highest payroll expense in the state of Massachusetts based on selected county.',
        style={'textAlign': 'left'}),
    html.P(
        'Users can click on one or multiple counties to study the top 50 departments with the highest total payroll expenses in the state of Massachusetts. Moreover, the pie chart would allow us to compare the proportion of total payroll earnings across the selected counties. Users who are interested in discovering high payroll expense on the department and county level could utilize this dashboard as an initial observation to generate idea for further research directions.',
        style={'textAlign': 'left'}),




    html.Div([html.P('The dropdown box is an interactive element where the users have the option to choose the counties they are interested in. It will generate a bar plot that reflects the sum of total earnings on the Y-axis, the top 50 department names with the highest pay in the county on the x-axis.'),

              html.H4('Countys to Display for Bar Plot:'),
              html.Div(dcc.Dropdown(
                        options=[{'label':'Suffolk', 'value':'Suffolk'},
                           {'label':'Norfolk', 'value': 'Norfolk'},
                           {'label':'Middlesex', 'value': 'Middlesex'},
                           {'label':'Worcester', 'value': 'Worcester'},
                           {'label':'Plymouth', 'value':  'Plymouth'},
                           {'label':'Essex', 'value':  'Essex'},
                           {'label':'Bristol', 'value':  'Bristol'},
                           {'label':'Barnstable', 'value': 'Barnstable'},
                           {'label':'Hampden', 'value':  'Hampden'},
                           {'label':'Dukes', 'value':  'Dukes'},
                           {'label':'Nantucket', 'value':  'Nantucket'},
                           {'label':'Berkshire', 'value':  'Berkshire'}],
                            value='Suffolk',
                            id = 'County_Dropdown'),style={'flex-direction':'row'}),
              html.Div(dcc.Graph(figure=fig, id='univ_plot'),style={'flex-direction':'row'}),],
                            style={'display': 'inline-block','width' : '45%', 'float' : 'left','margin': 'auto'}),


    html.Div([html.P('Users can use the check box element to compare the percentage of total earnings across counties in the pie chart and identify departments with the highest earnings in the table. For example, if we choose Suffolk and Middlesex as the base of our analysis, then we can see that Suffolk is 86.9 percent compared to the sum of both counties.'),
                html.H4('Countys to Display for Pie Chart:'),
                html.Div(dcc.Checklist(
                  options=[{'label':'Suffolk', 'value':'Suffolk'},
                           {'label':'Norfolk', 'value': 'Norfolk'},
                           {'label':'Middlesex', 'value': 'Middlesex'},
                           {'label':'Worcester', 'value': 'Worcester'},
                           {'label':'Plymouth', 'value':  'Plymouth'},
                           {'label':'Essex', 'value':  'Essex'},
                           {'label':'Bristol', 'value':  'Bristol'},
                           {'label':'Barnstable', 'value': 'Barnstable'},
                           {'label':'Hampden', 'value':  'Hampden'},
                           {'label':'Dukes', 'value':  'Dukes'},
                           {'label':'Nantucket', 'value':  'Nantucket'},
                           {'label':'Berkshire', 'value':  'Berkshire'}],
                  value=['Suffolk','Norfolk','Middlesex','Worcester','Plymouth','Essex',
                         'Bristol','Barnstable','Hampden','Dukes','Nantucket','Berkshire'],
                  id = 'County_checklist'),style={'width' : '15%','float' : 'left','display': 'inline-block','margin': 'auto'}),
                html.Div(dcc.Graph(figure=fig2, id='map_plot'),style={'width' : '60%','float' : 'right','display': 'inline-block','margin': 'auto'})],
             style={'display': 'inline-block','width' : '50%', 'float' : 'right','margin': 'auto'}),

    html.Div(children=[
                html.P('The table will also reflect the top 10 total earnings departments/county in Suffolk and Middlesex.'),
                html.H4(children='Top Earnings Table'),
                generate_table(df)], 
                id ='table_div'),


])
server = app.server

@app.callback(
    Output(component_id="map_plot", component_property="figure"),
    [Input(component_id="County_checklist", component_property="value")]
)
def update_map(counties):
    df1 = df_map[df_map.county.isin(counties)].sort_values('county')
    df1 = df1[['Total.Earnings','county']]
    fig2 = px.pie(df1,names='county',values='Total.Earnings')
    return fig2

@app.callback(
    Output(component_id="univ_plot", component_property="figure"),
    [Input(component_id="County_Dropdown", component_property="value")]
)
def update_plot(counties):
    df2 = df.loc[df['county']==counties].sort_values('Total.Earnings', ascending=False)
    df2 = df2[['Department', 'Total.Earnings', 'county']]
    fig = px.bar(df2,x="Department", y="Total.Earnings", color="county")
    return fig

@app.callback(
    Output(component_id="table_div", component_property="children"),
    [Input(component_id="County_checklist", component_property="value")]
)
def update_table(counties):
    x = df[df.county.isin(counties)].sort_values('Total.Earnings',ascending=False)
    return generate_table(x)

if __name__ == '__main__':
    app.run_server(debug=True)
