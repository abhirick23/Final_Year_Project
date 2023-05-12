#flask imports
from flask import Flask, render_template,request,redirect
#basic libraries
import pandas as pd
import numpy as np
# for paths and directories
import os
# code files or imports
from source_files.model_scripts.PE_file import func
from source_files.model_scripts.data_transformer import tranformer
from source_files.model_scripts.model_trainer import trainer
from source_files.model_scripts.viz_user_data import main
# for connecting database with flask
from flask_pymongo import PyMongo
from pymongo import MongoClient
#for checking email
import re
#for finding the time of operation
from datetime import datetime
import pytz
#for visualization
import dash
from dash import dcc
from dash import html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots


#creating a empty pandas dataframe



application = Flask(__name__)


'''
Connecting mongodb as a database for storing user data 
'''

application.config["SECRET_KEY"] = "3067fe7a54e944639f7f38304520381d42150d55"
application.config["MONGO_URI"] = "mongodb://localhost:27017/Final_Year_Project"
# mongo = MongoClient(application.config["MONGO_URI"])

mongo = PyMongo(application)

# db = mongo.Final_Year_Project
# collection = db.admin_data


'''
routes created from the next block of code
'''

@application.route('/')
def index():
    return render_template('home.html')


@application.route('/predictdata',methods=['GET','POST'])
def predict_datapoint():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        name = request.form.get("name")
        age = int(request.form.get("age"))
        country = request.form.get("country")
        city = request.form.get("city")
        email = request.form.get("email")
        occupation = request.form.get("occupation")
        organization = request.form.get("organization")
        results = None
        '''
        for the PE file processing and modelling
        '''
        # print(organization)
        file = request.files["input_file"]
        file_path = os.path.join("D:\Final_Year_Project\PE_files",file.filename)
        file.save(file_path)
        data  =  func(file_path)
        transformed_data = tranformer(data)
        results = trainer(transformed_data)
        
        '''
        checking the inputs for errors.
        
        '''
        
        try:
            if age < 11 or age > 75:
                raise ValueError
            if not re.match(r'^[a-zA-Z0-9._%+-]+@(gmail|yahoo|outlook)\.com$', email):
                raise ValueError
            
            '''
            Storing data into database
            
            '''
            if results >= 0.8:
                file_type = "malicious"
            elif results >0.5 and results<0.8:
                file_type = "not sure"
            else:
                file_type = "benign"
            mongo.db.user_data.insert_one({
                "User_Name":name,
                "User_Age":age,
                "Login_Country":country,
                "Login_City":city,
                "Email_Address":email,
                "Occupation":occupation,
                "Organization":organization,
                "Name_of_Portable_file":file.filename,
                "Time_of_Access": datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d %B %Y %H:%M:%S'),
                "File_type":file_type
            })
            
            '''
            
            Calling the dataset again for visualizations
            
            '''
            collection = mongo.db.user_data
            data = pd.DataFrame(list(collection.find()))
            main_data = pd.DataFrame()
            user_data = main(data)
            main_data = main_data.append(user_data,ignore_index=True)
            
            # main_data.to_csv("main_data.csv")
            main_data.to_csv(os.path.join('trial_files', 'main_data.csv'), index=False)
            return render_template('index.html',results = results)
        except ValueError:
            return render_template('home.html', error='Invalid input')

# @application.route("/visualize_data",methods = ['POST'])
# def visualize_data():
#     if request.method == 'POST':
#         results = request.form.get('results')
#         '''
        
#         Calling the dataset again for visualizations
        
#         '''
#         collection = mongo.db.user_data
#         data = pd.DataFrame(list(collection.find()))
        
#         user_data = main(data)
#         main_data = main_data.append(user_data,ignore_index=True)
        
#         # main_data.to_csv("main_data.csv")
#         main_data.to_csv(os.path.join('trial_files', 'main_data.csv'), index=False)

#     return render_template('index.html',results = float(results.strip('[]')))

'''

THE VISUALIZATION BEGINS

'''

app = dash.Dash(server=application, routes_pathname_prefix='/dash/',external_stylesheets=['/static/css_files/assets/index.css'])

# Load dataset
filepath = 'trial_files\main_data.csv'
df = pd.read_csv(filepath, index_col=False)

'''
initialize the making of the visualization
'''

# Create pie chart
pie_data = df.groupby(['Login_Country'])['Age_Groups'].nunique().reset_index()
pie_chart = px.pie(pie_data, values='Age_Groups', names='Login_Country', title='Count of Distinct Age_Groups by Login Country')

# Create map chart
map_chart = px.scatter_mapbox(df, lat='user_latitude', lon='user_longitude', hover_name='Login_Country',
                            size='User_Age', zoom=2.5, mapbox_style="carto-positron")

# create the line and cluster column chart
line_cluster_column_chart = make_subplots(specs=[[{"secondary_y": True}]])

line_cluster_data = df.groupby(['Occupation', 'Organization'])['hour_of_input'].agg(['nunique', 'sum']).reset_index()
line_cluster_data = line_cluster_data.sort_values(by='sum', ascending=False)

line_cluster_column_chart.add_trace(
    go.Bar(x = line_cluster_data['Organization'], y=line_cluster_data['nunique'], name='Count of Organization'),
    secondary_y=True,
)
line_cluster_column_chart.add_trace(
    go.Scatter(x = line_cluster_data['Organization'], y=line_cluster_data['sum'], name='Sum of Hour'),
    secondary_y=False,
)

#create the stacked bar chart
stack_bar_data = df.groupby(['Age_Group_Names', 'domain', 'File_type'])['domain'].count().reset_index(name='count')
stack_bar_chart = px.bar(stack_bar_data, x='domain', y='Age_Group_Names', color='File_type',orientation='h')

#create the funnel chart
funnel_data = df.groupby('Occupation')['Organization'].count().reset_index()
funnel_chart = px.funnel(funnel_data, x='Organization', y='Occupation')


'''

The layout 

'''
app.layout = html.Div([
    html.H1("Interactive Dashboard"),
    html.Div([
        # for the pie graph
        html.Div([
            dcc.Graph(
                id='pie-chart',
                figure=pie_chart
            ),
        ], style={'width': '40%'}),
        #for the map
        html.Div([
            dcc.Graph(
                id='map-chart',
                figure=map_chart
            ),
        ], style={'width': '60%'}),
    ], style={'display': 'flex'}),
    
    html.Div([
        # for line and clustered column chart
        html.Div([
            dcc.Graph(
                id='line-column-chart',
                figure=line_cluster_column_chart.update_layout(
                    legend=dict(orientation="h"),
                    yaxis2=dict(
                        title=dict(text="Count of Organization"),
                        side="right",
                        range=[0, 5],
                        overlaying="y",
                        tickmode="sync",
                    ),
                    yaxis=dict(
                        title=dict(text="Sum of Hour"),
                        side="left",
                        range=[0, 50],
                    ),
                )
            ),
        ],style={'width': '35%'}),
        #for stacked bar chart
        html.Div([
            dcc.Graph(
                id = 'stacked-bar-chart',
                figure=stack_bar_chart
                )
            ],style={'width':'35%'}),
        #for funnel chart
        html.Div([
            dcc.Graph(
                id='funnel-chart',
                figure=funnel_chart
            )
        ],style={'width':'30%'}),
    ], style={'display': 'flex','background-color':'blue'})

])



@app.callback(
    [Output('map-chart', 'figure'),
    Output('line-column-chart', 'figure'),
    Output('stacked-bar-chart', 'figure'),
    Output('funnel-chart', 'figure')],
    [Input('pie-chart', 'clickData')]
)
def update_all_charts(clickData):
    if clickData:
        login_country = clickData['points'][0]['label']
        filtered_df = df[df['Login_Country'] == login_country]
        avg_age = filtered_df['User_Age'].mean()

        # update map chart
        map_fig = px.scatter_mapbox(filtered_df, lat='user_latitude', lon='user_longitude', 
                                    hover_name='Login_Country', size='User_Age', zoom=2.5, 
                                    mapbox_style="carto-positron")
        map_fig.add_annotation(x=0.5, y=-0.15, showarrow=False, text=f'Average age: {avg_age:.2f}', 
                            font=dict(size=12, color='white'))

        # update line and clustered column chart
        line_cluster_data = filtered_df.groupby(['Occupation', 'Organization'])['hour_of_input'].agg(['nunique', 'sum']).reset_index()
        line_cluster_data = line_cluster_data.sort_values(by='sum', ascending=False)

        line_cluster_chart = make_subplots(specs=[[{"secondary_y": True}]])
        line_cluster_chart.add_trace(
            go.Bar(x=line_cluster_data['Organization'], y=line_cluster_data['nunique'], 
                name='Count of Organization', marker=dict(color='blue')),
            secondary_y=True
        )
        line_cluster_chart.add_trace(
            go.Scatter(x=line_cluster_data['Organization'], y=line_cluster_data['sum'], 
                    name='Sum of Hour', mode='lines+markers', marker=dict(color='red')),
            secondary_y=False
        )
        line_cluster_chart.update_layout(title='Count of Organization and Sum of Hour by Occupation in ' + login_country)

        # update stacked bar chart
        stack_bar_data = filtered_df.groupby(['Age_Group_Names', 'domain', 'File_type'])['domain'].count().reset_index(name='count')
        bar_chart = px.bar(stack_bar_data, x='domain', y='Age_Group_Names', color='File_type',
                                orientation='h', barmode='stack')
        bar_chart.update_layout(title='Count of Domains by Age Group and File Type in ' + login_country)

        # update funnel chart
        funnel_data = filtered_df.groupby('Occupation')['Organization'].count().reset_index()
        funnel_fig = px.funnel(funnel_data, x='Organization', y='Occupation', title='Count of Organization by Occupation in ' + login_country)

        return [map_fig, line_cluster_chart, bar_chart, funnel_fig]
    else:
        return [map_chart, line_cluster_column_chart, stack_bar_chart, funnel_chart]



'''
RUNNIG THE APPLICATION
'''

if __name__=="__main__":
    app.run(debug=True)