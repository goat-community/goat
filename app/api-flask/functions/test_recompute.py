from db import Database
from log import LOGGER
from psycopg2 import sql


# Create database class
db = Database()


def recompute_heatmap(scenario_id):
    """Function to recompute heatmap when network is changed."""
    import time
    start = time.time()

    speed = 1.33
    max_cost = 1200

    # """Get userid for particular scenario_id"""
    userid = db.select('''SELECT userid FROM scenarios WHERE scenario_id = %(scenario_id)s''', {
                       "scenario_id": scenario_id})[0][0]

    # """Clean tables and define changed grids"""
    db.perform('''DELETE FROM reached_edges_heatmap 
	WHERE scenario_id = %(scenario_id)s;

	DELETE FROM area_isochrones_scenario
	WHERE scenario_id = %(scenario_id)s;
	
	DROP TABLE IF EXISTS changed_grids;
	CREATE TEMP TABLE changed_grids AS 
	SELECT * FROM find_changed_grids(%(scenario_id)s,%(speed)s*%(max_cost)s);''', {"scenario_id": scenario_id, "speed": speed, "max_cost": max_cost})

    # """Select changed grids"""
    changed_grids = db.select(
        'SELECT starting_points, gridids, section_id FROM changed_grids;')

    # """Loop throuch section and recompute grids"""
    for i in changed_grids:
        print(i[2])

        db.perform('''SELECT pgrouting_edges_heatmap(%(max_cost)s, 
        %(starting_points)s, %(speed)s, %(gridids)s, 2, 
        'walking_standard',%(userid)s, %(scenario_id)s, %(section_id)s)''',
                   {"max_cost": [max_cost], "starting_points": i[0], "speed": speed, "gridids": i[1], "userid": userid, "scenario_id": scenario_id, "section_id": i[2]})

    return changed_grids


def test_heatmap(scenario_id, mode):
    query = sql.SQL("select {field} from {table} where {pkey} = %s").format(
        field=sql.Identifier('my_name'),
        table=sql.Identifier('some_table'),
        pkey=sql.Identifier('id'))

    db.select('''SELECT * FROM population_heatmap_geoserver(1,'default')''')


x = recompute_heatmap(1)


'''
FOR grid_id IN
    SELECT UNNEST(gridids) FROM changed_grids
LOOP
    PERFORM compute_area_isochrone(grid_id,scenario_id_input);
END LOOP;

SELECT ST_BUFFER(ST_UNION(geom),0.0014) 
INTO buffer_geom
FROM area_isochrones_scenario 
WHERE scenario_id = scenario_id_input;

DELETE FROM reached_pois_heatmap r
USING pois_userinput p
WHERE ST_Intersects(p.geom,buffer_geom)
AND r.gid = p.gid
AND r.scenario_id = scenario_id_input; 

PERFORM reached_pois_heatmap(buffer_geom, 0.0014, 'scenario', scenario_id_input);

UPDATE scenarios 
SET ways_heatmap_computed = TRUE 
WHERE scenario_id = scenario_id_input;
'''
