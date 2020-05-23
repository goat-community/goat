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

grid = 'grid_'+str(500)

sensitivities = [150000,200000,250000,300000,350000,400000,450000]

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

#Clean up edges and isochrones table 
cursor.execute('DELETE FROM edges; DELETE FROM isochrones;')
con.commit()
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

sql_create_reached_tables = '''
DROP TABLE IF EXISTS reached_vertices_heatmap;
CREATE TABLE reached_vertices_heatmap(
	id serial,
	node integer,
	cost smallint,
	geom geometry,
	grid_id integer,
	userid integer,
	modus integer,
	CONSTRAINT reached_vertices_heatmap_pkey PRIMARY KEY(id)
);
CREATE INDEX ON reached_vertices_heatmap(grid_id);
CREATE INDEX ON reached_vertices_heatmap(userid);
CREATE INDEX ON reached_vertices_heatmap USING gist(geom);

DROP TABLE IF EXISTS reached_pois_heatmap;
CREATE TABLE reached_pois_heatmap(
	id serial,
	poi_gid integer,
	amenity text,
	name text,
	cost smallint,
	geom geometry,
	grid_id integer,
	userid integer,
	scenario_id integer,
	CONSTRAINT reached_pois_heatmap_pkey PRIMARY KEY(id),
    FOREIGN KEY (poi_gid) REFERENCES pois_userinput (gid) ON DELETE CASCADE
);
CREATE INDEX ON reached_pois_heatmap(grid_id);
CREATE INDEX ON reached_pois_heatmap(poi_gid);
CREATE INDEX ON reached_pois_heatmap(userid);
CREATE INDEX ON reached_pois_heatmap USING gist(geom);
INSERT INTO reached_vertices_heatmap(node,cost,geom,grid_id)
SELECT node, cost, v_geom AS geom, objectid
FROM edges; 
'''
cursor.execute(sql_create_reached_tables)
con.commit()


for i in range(count_grids):
    cursor.execute('SELECT closest_pois_precalculated(0.0009,%i)' % (i+1))
    con.commit()


print('Expanding jsonb to columns is starting...')


sql_poi_categories = '''SELECT UNNEST(select_from_variable_container('pois_one_entrance')||select_from_variable_container('pois_more_entrances')) poi
ORDER BY poi;
'''
sql_index = '''UPDATE %s g SET %s = %s || x.object
FROM (
    SELECT grid_id, jsonb_build_object('%s',accessibility_index) as object
    FROM heatmap_dynamic(1,'{"%s":{"sensitivity":%s,"weight":1}}',1)
) x
WHERE g.grid_id = x.grid_id;'''
        
cursor.execute(sql_poi_categories)
poi_categories = cursor.fetchall()

for s in sensitivities:
    print(s)
    new_column = 'index_'+str(s)
    cursor.execute('ALTER TABLE %s DROP COLUMN IF EXISTS %s;' % (grid,new_column))
    cursor.execute('ALTER TABLE %s ADD COLUMN %s jsonb;' % (grid,new_column))
    cursor.execute('''UPDATE %s SET %s = '{}'::jsonb;''' % (grid,new_column))
    for p in poi_categories:
        p = p[0]
        cursor.execute(sql_index % (grid,new_column,new_column,p,p,s))
        
    cursor.execute('CREATE INDEX ON %s USING GIN(%s);' % (grid,new_column))           
    con.commit()
cursor.execute(sql_grid_population.replace('grid_size', str(grid_size)))

cursor.execute('DELETE FROM edges;')

con.commit()
con.close()
end = time.time()
print('Running the script took:')
print(end - start)

