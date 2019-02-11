import psycopg2
import time
import math
from variables_precalculate import *
from pathlib import Path
import yaml

start = time.time()

with open(str(Path.home())+"/app/config/goat_config.yaml", 'r') as stream:
    config = yaml.load(stream)
secrets = config["DATABASE"]
host = secrets["HOST"]
port = str(secrets["PORT"])
db_name = secrets["DB_NAME"]
user = secrets["USER"]
password = secrets["PASSWORD"]



con = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (db_name,user,host,password))
cursor = con.cursor()
grid_size = 500


def calculate_isochrones(grid_size):
	grid_size = str(grid_size)
	snap_tolerance = math.sqrt(2)*int(grid_size)
	cursor.execute(prepare_tables.replace('grid_size',grid_size))
	con.commit()
	cursor.execute('select grid_id, st_x(st_centroid(geom)), st_y(st_centroid(geom)) from grid_%s order by grid_id' % (grid_size))
	grid = cursor.fetchall()

	for i in grid:
	    grid_id = i[0]
	    x = i[1]
	    y = i[2]
	    insert_into = '''insert into precalculate_walking_%s select * from isochrones_precalculate(%s,%f,%f,%i,%f,%f,%i)''' % (grid_size,15,x,y,grid_id,83.33,0.99,snap_tolerance)
	    insert_into = insert_into.replace('grid_size',grid_size)
	    #print(insert_into)
	    
	    try:
	        cursor.execute(insert_into)
	        cursor.execute(final_sql.replace('grid_size',grid_size))
	        cursor.execute(thematic_data_sql.replace('grid_id_replace',str(grid_id)).replace('grid_size',grid_size))
	        con.commit()
	    except Exception as e:
	        print(e)
	        cursor.execute('rollback;')
	        continue




def calculate_index(grid_size):
    grid_size = str(grid_size)
    
   
    cursor.execute("select variable_array from variable_container where identifier = 'poi_categories'")
    pois=cursor.fetchall()[0][0]
    cursor.execute(sql_new_grid.replace('grid_size',grid_size))
    
    for i in sensitivities:
        
        sensitivity = str(i).split('.')[1]
        cursor.execute('ALTER TABLE precalculate_walking_%s add column index_0_%s jsonb' % (grid_size,sensitivity))
        cursor.execute('''UPDATE precalculate_walking_%s set index_0_%s='{"a":"first_value"}'::jsonb''' % (grid_size,sensitivity))
        
        sql_expand_json = 'select g.grid_id, '
        
        for x in public_transport_stops+pois:         
            cursor.execute(sql_calculate_accessibility.replace('amenity_type',x).replace('001',sensitivity).replace('grid_size',grid_size))
          
            con.commit()
        
        
    
        cursor.execute('''UPDATE precalculate_walking_100 set index_0_001= index_0_001- 'a' '''.replace('001',sensitivity).replace('100',grid_size))
        
        
        cursor.execute('ALTER TABLE grid_%s add column index_0_%s jsonb' % (grid_size,sensitivity))
        cursor.execute('''UPDATE grid_100 set index_0_001 = p.index_0_001 
                          from precalculate_walking_100 p where grid_100.grid_id = p.grid_id'''.replace('001',sensitivity).replace('100',grid_size))
        con.commit()
    con.commit()

calculate_isochrones(grid_size)   
calculate_index(grid_size)

cursor.execute(sql_grid_population.replace('grid_size',str(grid_size)))
con.commit()
con.close()
end = time.time()
print('Running the script took:')
print(end - start)