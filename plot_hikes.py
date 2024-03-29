#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 21:39:58 2021

@author: shaunhowe
"""

import os
import glob
import gpxpy
import folium
from folium import plugins
import pandas as pd
import numpy as np


def process_gpx_to_df(file_name):
    '''
    '''
    gpx = gpxpy.parse(open(file_name))
 
    ## 1: make DataFrame
    track = gpx.tracks[0]
    segment = track.segments[0]
    # Load the data into a Pandas dataframe (by way of a list)
    data = []
    segment_length = segment.length_3d()
    for point_idx, point in enumerate(segment.points):
        data.append([point.longitude, point.latitude,point.elevation,
                     point.time, segment.get_speed(point_idx)])
    
    
    columns = ['Longitude', 'Latitude', 'Altitude', 'Time', 'Speed']
    gpx_df = pd.DataFrame(data, columns=columns)
 
    ## 2: make points tuple for lin
    ## TODO: Look into doing this loop more efficiently
    points = []
    for track in gpx.tracks:
        for segment in track.segments: 
            for point in segment.points:
                points.append([point.latitude, point.longitude])
                # points.append(tuple([point.latitude, point.longitude]))
 
    return gpx_df, points


def get_gpx_dirs(in_path, activity_list):
    '''
    '''
    
    gpx_dirs = glob.glob(in_path, recursive='True')
    
    gpx_dict = {}
    
    ## loop through activity directories
    for i in range(len(gpx_dirs)):
        activity = gpx_dirs[i].split('/')[-2]
        
        ## only plot activities from specified list
        if activity in activity_list:
            ## get the GPX files in each activity directory
            activity_glob = glob.glob(os.path.join(gpx_dirs[i], '*.gpx'))

            print(activity)
            if activity not in gpx_dict:
                gpx_dict[activity] = {'lat_mean':[], 'lon_mean':[], 'points':[]}

            ## loop through GPX files and save to a dictionary of activities
            for file in activity_glob:
                gpx_df, points = process_gpx_to_df(file)

                gpx_dict[activity]['lon_mean'].append(gpx_df.Longitude.mean())
                gpx_dict[activity]['lat_mean'].append(gpx_df.Latitude.mean())
                gpx_dict[activity]['points'].append(points)


    return gpx_dict
        

def create_map(lat_mean, lon_mean):
    '''
    '''
    
    # mymap = folium.Map( location=[df.Latitude.mean(), df.Longitude.mean() ], zoom_start=6, tiles=None)
    mymap = folium.Map( location=[lat_mean, lon_mean], zoom_start=6, tiles=None)
    folium.TileLayer('openstreetmap', name='OpenStreet Map').add_to(mymap)
    
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}', attr='Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC', name='Nat Geo Map').add_to(mymap)
    # folium.TileLayer('http://tile.stamen.com/terrain/{z}/{x}/{y}.jpg', attr='terrain-bcg', name='Terrain Ma').add_to(mymap)
    
    return mymap
    

def plot_points_on_map(mymap, gpx_dict, map_name):
    '''
    '''
    
    print('Creating Strava Point Map')
    
    ## loop through activity GPX and add activitiy layers to the map
    for act in gpx_dict:
        if act == 'hike':
            activity_color = 'orange'
        elif act == 'kayak':
            activity_color = 'navy'
        elif act == 'bike':
            activity_color = 'black'
        elif act == 'run':
            activity_color = 'red'
        elif act == 'ebike':
            activity_color = 'yellow'
            
        ## create activity map
        fg_act = folium.FeatureGroup(name=act)
        
        ## plot activity feature
        fg_act.add_child(folium.PolyLine(gpx_dict[act]['points'], color=activity_color, weight=4.5, opacity=.5))
        mymap.add_child(fg_act)
        
    folium.LayerControl().add_to(mymap)
        
    mymap.save(map_name)

def plot_heatmap(mymap, gpx_dict, map_name):
    '''
    '''
    
    print('Creating Strava Heatmap')
    
    ## loop through activity GPX and add activitiy layers to the map
    for act in gpx_dict:
        
        ## create activity heatmap map
        fg_heat = folium.FeatureGroup(name=act+' heatmap')

        heat_data = [item for sublist in gpx_dict[act]['points'] for item in sublist]

        
        ## plot feature
        fg_heat.add_child(plugins.HeatMap(heat_data, show=False))#, radius=15))
        mymap.add_child(fg_heat)
        
        
    folium.LayerControl().add_to(mymap)
        
    mymap.save(map_name)


if __name__ == '__main__':

    gpx_dirs = r'/path/to/strava/activities/*/'
    
    gpx_dict = get_gpx_dirs(gpx_dirs, ['hike', 'kayak'])


    mymap1 = create_map(np.mean(gpx_dict['hike']['lat_mean']), np.mean(gpx_dict['hike']['lon_mean']))
    mymap2 = create_map(np.mean(gpx_dict['hike']['lat_mean']), np.mean(gpx_dict['hike']['lon_mean']))
    
    # plot_on_map(mymap, gpx_dict['hike']['points'], 'mymap.html')
    plot_points_on_map(mymap1, gpx_dict, 'mymap_points_new.html')
    plot_heatmap(mymap2, gpx_dict, 'mymap_heat_new.html')
