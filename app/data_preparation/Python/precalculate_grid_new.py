import psycopg2
import time
import math
from variables_precalculate import *
from pathlib import Path
import yaml


step = 100
grid_size = 500
start = time.time()

#with open(str(Path.home())+"/app/config/goat_config.yaml", 'r') as stream:

with open("/home/ga73buy/Schreibtisch/goat_neu/app/config/goat_config.yaml", 'r') as stream:
    config = yaml.load(stream)
secrets = config["DATABASE"]
host = secrets["HOST"]
port = '65432'#str(secrets["PORT"])
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

con.close()

end = time.time()
print('Running the script took:')
print(end - start)

