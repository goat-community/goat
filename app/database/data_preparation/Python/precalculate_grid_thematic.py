import psycopg2
import time
import math
from variables_precalculate import *
from pathlib import Path
import yaml

#Step defined the bulk size of the heatmap calculation
step = 150
#Grid size defines the size of each grid
grid_size = 500
beta = -0.003
grid = 'grid_'+str(500)

sensitivities = [-0.004,-0.0035,-0.003,-0.0025,-0.002,-0.0015,-0.001]

start = time.time()
with open("/opt/config/goat_config.yaml", 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
secrets = config["DATABASE"]
host = secrets["HOST"]
port = str(secrets["PORT"])
db_name = secrets["DB_NAME"]
user = secrets["USER"]
password = secrets["PASSWORD"]


con = psycopg2.connect("dbname='%s' user='%s' port = '%s' host='%s' password='%s'" % (
    db_name, user, port, host, password))
cursor = con.cursor()


cursor.execute(prepare_tables.replace('grid_size', str(grid_size)))
con.commit()

sql_ordered_grid = '''DROP TABLE IF EXISTS grid_ordered;
CREATE temp TABLE grid_ordered AS 
SELECT starting_points, grid_id
FROM (
    SELECT ARRAY[ST_X(st_centroid(geom))::numeric,ST_Y(ST_Centroid(geom))::numeric] starting_points, grid_id 
    FROM %s 
    ORDER BY st_centroid(geom)
) x;
ALTER TABLE grid_ordered ADD COLUMN id serial;
ALTER TABLE grid_ordered ADD PRIMARY key(id);'''

cursor.execute(sql_ordered_grid % grid)
con.commit()

cursor.execute('SELECT count(*) FROM grid_ordered;')
count_grids = cursor.fetchall()[0][0]

print('Bulk calculation is starting...')

lower_limit = 1
while lower_limit < count_grids:
    print(lower_limit)
 
    sql_bulk_calculation = '''
        WITH x AS 
    	(
    		SELECT array_agg(starting_points) AS array_starting_points, array_agg(grid_id) AS grid_ids
    		FROM grid_ordered 
    		WHERE id BETWEEN %i AND %i
    	)
    		SELECT precalculate_grid(1,'%s',15, x.array_starting_points,5,x.grid_ids,1,'walking_standard') 
    		FROM x;'''
    cursor.execute(sql_bulk_calculation % (lower_limit, lower_limit+step-1, grid))
    con.commit()
    lower_limit = lower_limit + step



print('Expanding jsonb to columns is starting...')

sql_poi_categories = '''SELECT UNNEST(select_from_variable_container('pois_one_entrance')||select_from_variable_container('pois_more_entrances')) poi
ORDER BY poi;
'''
sql_index = '''UPDATE %s g SET %s = %s || x.object
FROM (
    SELECT grid_id, jsonb_build_object('%s',accessibility_index) as object
    FROM heatmap_dynamic('[{"%s":{"sensitivity":%s,"weight":1}}]')
    WHERE accessibility_index <> 0
) x
WHERE g.grid_id = x.grid_id;'''
        
cursor.execute(sql_poi_categories)
poi_categories = cursor.fetchall()

for s in sensitivities:
    print(s)
    new_column = 'index_'+str(s).split('.')[1]
    cursor.execute('ALTER TABLE %s DROP COLUMN IF EXISTS %s;' % (grid,new_column))
    cursor.execute('ALTER TABLE %s ADD COLUMN %s jsonb;' % (grid,new_column))
    cursor.execute('''UPDATE %s SET %s = '{}'::jsonb;''' % (grid,new_column))
    for p in poi_categories:
        p = p[0]
        cursor.execute(sql_index % (grid,new_column,new_column,p,p,s))
        
    cursor.execute('CREATE INDEX ON %s USING GIN(%s);' % (grid,new_column))           
    con.commit()
cursor.execute(sql_grid_population.replace('grid_size', str(grid_size)))

con.commit()
con.close()
end = time.time()
print('Running the script took:')
print(end - start)

