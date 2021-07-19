import time
import math
from variables_precalculate import *
from db.db import Database
db_conn = Database()


#Step defined the bulk size of the heatmap calculation
step = 200
#Grid size defines the size of each grid
grid_size = 150

start = time.time()

db_conn.perform(prepare_tables % grid_size)

sql_ordered_grid = '''
DROP TABLE IF EXISTS compute_sections; 
CREATE TABLE compute_sections AS
WITH b AS 
(
	SELECT ST_BUFFER(geom::geography, 1600)::geometry AS geom 
	FROM study_area_union 
),
g AS 
(
	SELECT (ST_DUMP(makegrid_2d(ST_BUFFER(geom::geography, 1600)::geometry, 2000, 2000))).geom
	FROM b
)
SELECT ROW_NUMBER() OVER() AS section_id, g.geom 
FROM b, g
WHERE ST_Intersects(b.geom,g.geom);

CREATE INDEX ON compute_sections USING GIST(geom);

DROP TABLE IF EXISTS grid_ordered;
CREATE TABLE grid_ordered AS 
SELECT starting_points, centroid, geom, grid_id, section_id, ROW_NUMBER() over() AS id 
FROM (
    SELECT ARRAY[ST_X(st_centroid(g.geom))::numeric,ST_Y(ST_Centroid(g.geom))::numeric] starting_points, st_centroid(g.geom) centroid, g.geom, g.grid_id, c.section_id 
    FROM grid_heatmap g, compute_sections c 
    WHERE ST_Intersects(st_centroid(g.geom),c.geom)
    ORDER BY section_id
) x;
ALTER TABLE grid_ordered ADD PRIMARY key(grid_id);
CREATE INDEX ON grid_ordered USING GIST(centroid);'''

db_conn.perform(sql_ordered_grid)

sql_edges_heatmap = '''
DROP TABLE IF EXISTS reached_edges_heatmap;
CREATE TABLE reached_edges_heatmap 
(
	id serial, 
	edge bigint,
	gridids integer[],
	start_cost smallint[],
	end_cost smallint[],
	userid integer,
	scenario_id integer,
	geom geometry,
	start_perc float,
	end_perc float,
	partial_edge boolean,
	CONSTRAINT reached_edges_heatmap_pkey PRIMARY KEY (id)
);

CREATE INDEX ON reached_edges_heatmap (userid);
CREATE INDEX ON reached_edges_heatmap (edge);
CREATE INDEX ON reached_edges_heatmap (scenario_id);
CREATE INDEX ON reached_edges_heatmap USING gist(geom);

CREATE INDEX ON reached_edges_heatmap USING gin (gridids gin__int_ops);

DROP TABLE IF EXISTS reached_pois_heatmap;
CREATE TABLE reached_pois_heatmap (
	id serial,
	gid integer,
	amenity text,
	name text,
	gridids integer[],
	arr_cost integer[],
	edge integer,
	fraction float,
	accessibility_indices integer[],
	userid integer,
	scenario_id integer,
	CONSTRAINT reached_pois_heatmap_pkey PRIMARY KEY (id)
);
ALTER TABLE reached_pois_heatmap ADD CONSTRAINT 
reached_pois_heatmap_gid_fkey FOREIGN KEY(gid)
REFERENCES pois_userinput(gid)
ON DELETE CASCADE; 

CREATE INDEX ON reached_pois_heatmap USING gin (gridids gin__int_ops);
CREATE INDEX ON reached_pois_heatmap USING gin (arr_cost gin__int_ops);
CREATE INDEX ON reached_pois_heatmap (edge);
CREATE INDEX ON reached_pois_heatmap (gid);
CREATE INDEX ON reached_pois_heatmap (amenity);
'''
print('Bulk calculation is starting...')

db_conn.perform(sql_edges_heatmap)

section_ids = db_conn.select('SELECT array_agg(section_id) FROM (SELECT DISTINCT section_id FROM grid_ordered ORDER BY section_id) x;')[0][0]

sql_bulk_calculation = '''WITH x AS 
(
	SELECT array_agg(starting_points) AS array_starting_points, array_agg(grid_id) AS grid_ids
	FROM grid_ordered 
	WHERE section_id = %i
)
SELECT pgrouting_edges_heatmap(ARRAY[1200.], x.array_starting_points, 1.33, x.grid_ids, 1, 'walking_standard',0,0,%i)
FROM x;
'''

#Loop for routing calculation
for i in section_ids:
	print('Compute routing section: %s' % str(i))
	db_conn.perform(sql_bulk_calculation % (i, i))

time_routing = time.time()-start
print('Routing calculation has finished after: %s s' % (time_routing))


#Loop for closest POIs calculation (needs to be executed after routing is completed)
for i in section_ids: 
	print('Compute reached pois section: %s' % str(i))
	db_conn.perform('''SELECT reached_pois_heatmap(geom,0.0014,'default',0) 
	FROM compute_sections 
	WHERE section_id = %s
	''' % str(i))

print('Closest POIs calculation has finished after: %s s' % (time.time()-start-time_routing))

#Compute Accessibility Values
db_conn.perform('SELECT compute_accessibility(0)')

#Loop for isochrone area calculation
gridids = db_conn.select('SELECT grid_id FROM grid_heatmap;')

for i in gridids:
	i = i[0]
	db_conn.perform(f'''SELECT compute_area_isochrone({i},0,1,0);''')	

db_conn.perform(sql_grid_population)

end = time.time()
print('Running the script took:')
print(end - start)

