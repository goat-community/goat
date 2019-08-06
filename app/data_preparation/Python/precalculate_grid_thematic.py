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


cursor.execute(prepare_tables.replace('grid_size', str(grid_size)))
con.commit()

sql_ordered_grid = '''DROP TABLE IF EXISTS grid_ordered;
CREATE temp TABLE grid_ordered AS 
SELECT starting_points, grid_id
FROM (
    SELECT ARRAY[ST_X(st_centroid(geom))::numeric,ST_Y(ST_Centroid(geom))::numeric] starting_points, grid_id 
    FROM grid_500 
    ORDER BY st_centroid(geom)
) x;
ALTER TABLE grid_ordered ADD COLUMN id serial;
ALTER TABLE grid_ordered ADD PRIMARY key(id);'''

cursor.execute(sql_ordered_grid)
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
    		SELECT precalculate_grid('grid_500',15, x.array_starting_points, 5, x.grid_ids) 
    		FROM x;'''
    cursor.execute(sql_bulk_calculation % (lower_limit, lower_limit+step-1))
    con.commit()
    lower_limit = lower_limit + step



print('Expanding jsonb to columns is starting...')

sql_poi_categories = '''SELECT poi FROM (
SELECT unnest(variable_array::text[]) poi FROM variable_container WHERE identifier = 'poi_categories' 
) x 
ORDER BY poi;
'''

cursor.execute(sql_poi_categories)
poi_categories = cursor.fetchall()




for i in poi_categories:
    cursor.execute('ALTER TABLE %s ADD COLUMN %s numeric[];' % (grid,i[0]))
    cursor.execute('''UPDATE %s set %s= jsonb_arr2text_arr((pois ->> '%s')::jsonb)::numeric[];''' % (grid,i[0],i[0]))

print('Precalculate index is starting...')

column_name_index = str(-beta).replace('.','_')
cursor.execute('ALTER TABLE %s ADD COLUMN index_%s jsonb;' % (grid,column_name_index))
cursor.execute('''UPDATE %s SET index_%s = '{}'::jsonb;''' % (grid,column_name_index))

sql_compute_index = '''
UPDATE %s SET index_%s = index_%s || jsonb_build_object('%s',x.accessibility_index)
FROM (
     SELECT grid_id, accessibility_index 
    from heatmap_dynamic('[{"%s":{"sensitivity":%s,"weight":1}}]')
    WHERE accessibility_index <> 0
) x 
WHERE %s.grid_id = x.grid_id
'''

for i in poi_categories:
    cursor.execute(sql_compute_index % (grid,column_name_index,column_name_index,i[0],i[0],beta,grid))

cursor.execute(sql_grid_population.replace('grid_size', str(grid_size)))

con.commit()
con.close()
end = time.time()
print('Running the script took:')
print(end - start)

