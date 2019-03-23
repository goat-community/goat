#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 15:16:43 2019

@author: ga73buy
"""

import psycopg2
import yaml
from pathlib import Path
with open(str(Path.home())+"/Schreibtisch/goat/app/config/goat_config.yaml", 'r') as stream:
    config = yaml.load(stream)
secrets = config["DATABASE"]
host = secrets["HOST"]
port = str(secrets["PORT"])
db_name = secrets["DB_NAME"]
user = secrets["USER"]
password = secrets["PASSWORD"]



con = psycopg2.connect("dbname='%s' user='%s' port ='65432' host='%s' password='%s'" % (db_name,user,host,password))
cursor = con.cursor()


sql_vertices_to_check = '''with x as (
                            select count(id) , id 
                            from 
                            (
                            	select source as id 
                            	from ways
                            	UNION ALL 
                            	select target as id
                            	from ways
                            ) x
                            group by id
                            )
                            select x.id 
                            FROM x 
                            WHERE x.count=2'''
                            
cursor.execute(sql_vertices_to_check)
vertices = cursor.fetchall()

ids_to_merge=[]

for i in vertices:
    cursor.execute('SELECT id,geom,class_id, length_m FROM ways WHERE source = %i OR target = %i' % (i[0],i[0]))
    links = cursor.fetchall()
    if (links[0][2] == links[1][2]) and (links[0][3] < 40 or links[1][3] < 40):
        ids_to_merge.append(links[0][0])
        ids_to_merge.append(links[1][0])
        print(links[0][3])
        print(links[1][3])
        print('#########################')
        
                 

'''WITH x AS (
	SELECT ST_Union(geom) geom, array_agg(class_id) class_ids, array_agg(length_m) lengths
	FROM ways
	WHERE SOURCE = 79532
	OR target = 79532
)
SELECT geom, CASE WHEN class_ids[1] = class_ids[2] THEN class_ids ELSE '{0}' END,
CASE WHEN lengths[1] < 20 OR lengths[2] < 20 THEN lengths ELSE '{0}' END
FROM x 
'''
           
