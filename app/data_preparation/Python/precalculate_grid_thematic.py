import psycopg2
import time
import math
from variables_precalculate import *
from pathlib import Path
import yaml
from random import randint

start = time.time()

with open(str(Path.home())+"/app/config/goat_config.yaml", 'r') as stream:
    config = yaml.load(stream)
secrets = config["DATABASE"]
host = secrets["HOST"]
port = str(secrets["PORT"])
db_name = secrets["DB_NAME"]
user = secrets["USER"]
password = secrets["PASSWORD"]


con = psycopg2.connect("dbname='%s' user='%s' port = '%s' host='%s' password='%s'" % (
    db_name, user, port, host, password))
cursor = con.cursor()
grid_size = 500


def calculate_isochrones(grid_size):
    grid_size = grid_size
    snap_tolerance = math.sqrt(2)*grid_size
    cursor.execute(prepare_tables.replace('grid_size', str(grid_size)))
    con.commit()
    cursor.execute(
        'select grid_id, st_x(st_centroid(geom)), st_y(st_centroid(geom)) from grid_%s order by grid_id' % (grid_size))
    grid = cursor.fetchall()
    for i in grid:
        grid_id = int(i[0])
        x = i[1]
        y = i[2]
        objectid = randint(1, 10000000)
        insert_into = '''
        DROP TABLE IF EXISTS iso_precalculate;
        CREATE temp TABLE iso_precalculate AS WITH iso AS ( 
        SELECT *, %i
        FROM isochrones(999999,15,%f,%f,1,%f,%f,1,%i,1)
        )
        ,
        upt AS (
        INSERT INTO isochrones(userid,id,step,geom,objectid) SELECT * FROM iso
        )
        SELECT * FROM iso;
        UPDATE grid_%s SET isochrone_gid = i.gid FROM isochrones i 
        WHERE i.objectid = %i	
        AND grid_id = %i;''' % (objectid, x, y, 83.33, 1, objectid,str(grid_size), objectid, grid_id)
  
        sql_update_grid= '''UPDATE grid_%i set area_isochrone = st_area(i.geom::geography)
               from isochrones i
               where isochrone_gid=i.gid;
               UPDATE grid_%i SET pois = i.pois::jsonb 
               FROM isochrones i WHERE i.objectid = %i
               AND grid_id = %i''' % (grid_size,grid_size,objectid,grid_id)
        try:
            cursor.execute(insert_into)
            cursor.execute('SELECT isochrone_gid FROM grid_500 WHERE grid_id = %i' % grid_id)
            isochrone_gid = cursor.fetchall()
            isochrone_gid = isochrone_gid[0][0]
            print(isochrone_gid)
            cursor.execute('SELECT * FROM thematic_data_json(%i)' % (isochrone_gid))
            
            cursor.execute(sql_update_grid)
            con.commit()
        except Exception as e:
        	print(e)
        	cursor.execute('rollback;')
        continue


def calculate_index(grid_size):
    grid_size = int(grid_size)

    cursor.execute(
        "select variable_array from variable_container where identifier = 'poi_categories'")
    pois = cursor.fetchall()[0][0]

    for sensitivity in sensitivities:

        cursor.execute('ALTER TABLE grid_%i add column index_0_%s jsonb' % (grid_size, sensitivity))
        con.commit()
        cursor.execute('''UPDATE grid_%s set index_0_%s='{"a":"first_value"}'::jsonb''' % (grid_size, sensitivity))

        sql_expand_json = 'select g.grid_id, '

        for poi in pois:
            cursor.execute(sql_calculate_accessibility % (float('0.'+sensitivity),grid_size,poi,poi,grid_size,sensitivity,sensitivity,grid_size))
            con.commit()

        cursor.execute('''UPDATE grid_%i set index_0_%s= index_0_%s - 'a' ''' % (grid_size,sensitivity,sensitivity))
        con.commit()


calculate_isochrones(grid_size)
calculate_index(grid_size)

cursor.execute(sql_grid_population.replace('grid_size', str(grid_size)))
con.commit()
con.close()
end = time.time()
print('Running the script took:')
print(end - start)
