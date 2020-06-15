#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 09:30:26 2020

@author: Elias Pajares

This scripts is simplifying DEMs on high resolution to a lower resolution.
It was tested with a DEM 1m x 1m to DEM 5m x 5m, 10m x 10m, 20m x 20m.
"""

import math
import os 
import sys 

sys.path.append('/opt/scripts')

from db_functions import DB_connection
from db_functions import ReadYAML

aggregation_level = 10

thresholds_levels = {5:[(3/5),3000], 10:[0.5,5000], 20:[(0.5),10000]}
column_threshold, row_threshold = thresholds_levels[aggregation_level]

try:
    os.mkdir('/opt/data/dem_agg/')
except FileExistsError:
    print ('Folder data/dem_agg already exists!')
    
def dgm_width(path_name):
    f =  open(path_name)

    lon = ''
    cnt = 0
    for line in f:
        cnt += 1
        next_lon = line.replace("\n","").split(' ')[1]
        if lon != next_lon and cnt != 1:
            break
        lon = next_lon
    return cnt - 1 

def file_length(path_name):
    f =  open(path_name)
    for i, l in enumerate(f):
        pass
    return i + 1

def conversion(path_name, write_path_name,w_width,f_length):

    f_read =  open(path_name)
    f_write =  open(write_path_name,'a')
    
    first_coordinate = f_read.readline().split(' ')[0:2]
    cnt = 0
    for line in f_read:
        cnt += 1 
        rest_by_five = round(((cnt/aggregation_level) % 1),1)
        difference_rows = math.ceil(cnt/(aggregation_level * w_width)) * ((aggregation_level * w_width)) - (math.floor(cnt/w_width) * w_width)
        
        if rest_by_five == column_threshold and difference_rows == row_threshold:
            f_write.write(line)
            
    last_coordinate = line.split(' ')[0:2]
    
    f_write.close()
    
    new_filename = '%s_%s_%s_%s_resolution_%s.txt' % (str(first_coordinate[0]),str(first_coordinate[1]),str(last_coordinate[0]),str(last_coordinate[1]),aggregation_level)
    os.rename(write_path_name, '/opt/data/dem_agg/'+new_filename)

def bulk_conversion():
    for i in os.listdir('/opt/data/dem/'):
        path_name = '/opt/data/dem/'+i
        write_path_name = '/opt/data/dem_agg/'+i
    
        try:
            conversion(path_name,write_path_name,dgm_width(path_name),file_length(path_name))
        except:
            print('Something went wrong with file:' + path_name)
bulk_conversion()

os.system('raster2pgsql -s 25832 -I -c -C -M /opt/data/dem_agg/*.txt -F -t 100x100 public.dem > dem.sql')

def import_as_points():
    db_name,user,host,port,password = ReadYAML().db_credentials()
    db = DB_connection(db_name,user,host,port,password)
    con,cursor = db.con_psycopg()

    sql_create_table = '''DROP TABLE IF EXISTS dem_points; 
    CREATE TABLE dem_points (x integer,y integer,z NUMERIC, geom geometry);'''

    cursor.execute(sql_create_table)

    for i in os.listdir('/opt/data/dem_agg'):
        sql_import = f'''COPY dem_points(x,y,z) 
        FROM '/opt/data/dem_agg/{i}' DELIMITER ' ';'''
        cursor.execute(sql_import)

    cursor.execute('UPDATE dem_points SET geom = ST_Transform(ST_setsrid(st_makepoint(x,y),25832),4326);')

    con.commit()



   