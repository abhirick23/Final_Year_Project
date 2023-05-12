from geopy.geocoders import Nominatim
import pandas as pd
# from pymongo import MongoClient
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

# client = MongoClient('localhost', 27017)
# db = client['Final_Year_Project']
# collection = db['user_data']

# # Retrieve data from the MongoDB collection
# data = pd.DataFrame(list(collection.find()))

# function to get the latitude and longitude of the area of the user
def get_lat_long(city, country):
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.geocode(f"{city}, {country}")
    if location:
        return (location.latitude, location.longitude)
    else:
        return (None,None)
    
#function to get the grouped columns for visualization
# def create_grouped_data(data, group_cols):
#     # Define the fixed column for file_type
#     file_type_col = 'File_type'

#     # Group the data by the specified group columns and file_type
#     grouped_data = data.groupby(group_cols + [file_type_col]).size().reset_index(name='count')

#     # Return the grouped data
#     return grouped_data,group_cols

# #creating the visualization
# def plot(data,columns):
#     colors = ['#8B0000', 'Blue', 'Green', '#4B0082']
#     fig = go.Figure(go.Bar(
#         x=data['File_type'],
#         y=data['count'],
#         text=data[columns].apply(lambda row: '<br>'.join(f"{col}: {val}" for col, val in row.items()), axis=1),
#         hovertemplate='%{text}<br>File type: %{x}<br>Count: %{y}<extra></extra>',
#         marker=dict(
#             color=[colors[i % len(colors)] for i in range(len(data))], # Set the colors for each bar
#             line=dict(color='gray', width=1), # Set the outline color and width for each bar
#         )
#     ))

    # Set the chart title and axis labels
    fig.update_layout(title='File Types Count', xaxis_title='File Types', yaxis_title='Count')

    # Show the chart
    # fig.show()
    return fig


#the main function
def main(org_data):
    
    # finiding the latitude and longitude
    org_data["user_latitude"] = org_data.apply(lambda org_data: get_lat_long(org_data["Login_City"], org_data["Login_Country"])[0], axis=1)
    org_data["user_longitude"] = org_data.apply(lambda org_data: get_lat_long(org_data["Login_City"], org_data["Login_Country"])[1], axis=1)
    
    bins = [11, 19, 26, 41, 56, 76]
    labels = ['11-18', '19-25', '26-40', '41-55', '56-75']
    org_data['Age_Groups'] = pd.cut(org_data['User_Age'], bins=bins, labels=labels, include_lowest=True)
    
    #finding the hour at which the file was inputted
    org_data["hour_of_input"] = pd.to_datetime(org_data["Time_of_Access"]).dt.hour
    
    #putting names to the age groups
    age_group_map = {
    '11-18': 'Children',
    '19-25': 'Adolescents',
    '26-40': 'Young_Adults',
    '41-55': 'Adults',
    '56-75': 'Experienced_Citizens'
    }
    org_data['Age_Group_Names'] = org_data['Age_Groups'].apply(lambda x: age_group_map[x])
    
    #spliiting the email into parts
    org_data[['username', 'domain', 'extension']] = org_data['Email_Address'].str.split('@|\.', expand=True)[[0, 1, 2]]
    
    # grouped_data,inputted_cols = create_grouped_data(org_data,input_fields)
    
    return org_data


# print(main(data))