import psycopg2
import time
import math
from variables_precalculate import *
from db_functions import ReadYAML
from db_functions import DB_connection
from pathlib import Path
import yaml

#Step defined the bulk size of the heatmap calculation
step = 150
#Grid size defines the size of each grid
grid_size = 500

grid = 'grid_'+str(500)

sensitivities = [150000,200000,250000,300000,350000,400000,450000]

start = time.time()

db_name,user,host,port,password = ReadYAML().db_credentials()
db = DB_connection(db_name,user,host,port,password)

con,cursor = db.con_psycopg()

cursor.execute(prepare_tables.replace('grid_size', str(grid_size)))

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


sql_edges_heatmap = '''
DROP TABLE IF EXISTS reached_edges_heatmap;
CREATE TABLE reached_edges_heatmap 
(
	edge bigint,
	gridids integer[],
	start_cost smallint[],
	end_cost smallint[],
	userid integer,
	scenario_id integer,
	geom geometry,
	partial_edge boolean
);
'''

cursor.execute(sql_edges_heatmap)

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
		SELECT pgrouting_edges_heatmap(ARRAY[900.], x.array_starting_points, 1.33, 1, 0, x.grid_ids,%i, 1, 'walking_standard')
		FROM x;'''
    cursor.execute(sql_bulk_calculation % (lower_limit, lower_limit+step-1, lower_limit-1))
    con.commit()
    lower_limit = lower_limit + step

sql_indices = '''
ALTER TABLE reached_edges_heatmap ADD COLUMN id serial;
ALTER TABLE reached_edges_heatmap ADD PRIMARY KEY(id);
CREATE INDEX ON reached_edges_heatmap USING gist(geom);
'''
cursor.execute(sql_indices)
con.commit()
con.close()
end = time.time()
print('Running the script took:')
print(end - start)

