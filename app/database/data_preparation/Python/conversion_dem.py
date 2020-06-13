#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 09:30:26 2020

@author: Elias Pajares
"""

import math
import os 
import sys 

sys.path.append('/opt/scripts')

from db_functions import DB_connection
from db_functions import ReadYAML

aggregation_level = 10

thresholds_levels = {5:[(3/5),3000], 10:[0.5,5000]}
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
    f_write =  open(write_path_name,'w')
    
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
    
        conversion(path_name,write_path_name,dgm_width(path_name),file_length(path_name))

bulk_conversion()





   