from db.db import Database
from psycopg2 import sql

# Create database class
db = Database()


sql_geojson = '''SELECT jsonb_build_object(
		'type',     'FeatureCollection',
		'features', jsonb_agg(features.feature)
)::text
FROM (
SELECT jsonb_build_object(
	'type',       'Feature',
	'geometry',   ST_AsGeoJSON(geom,5)::jsonb,
	'properties', to_jsonb(inputs) - 'geom'
) AS feature 
FROM (SELECT * FROM heatmap_temp) inputs) features;'''



def heatmap_gravity(amenities_json,modus_input,scenario_id_input):
    db.perform('DROP TABLE IF EXISTS heatmap_temp;')

    db.perform('''CREATE TEMP TABLE heatmap_temp AS 
    SELECT percentile_accessibility AS score, geom 
    FROM heatmap_gravity(%(amenities_json)s::jsonb,%(modus_input)s,%(scenario_id_input)s);''',
    {"amenities_json": amenities_json, "modus_input": modus_input, "scenario_id_input": scenario_id_input})
    
    return db.select(sql_geojson)[0][0]

def heatmap_population(scenario_id_input, modus_input):
    db.perform('DROP TABLE IF EXISTS heatmap_temp;')

    db.perform('''CREATE TEMP TABLE heatmap_temp AS 
    SELECT percentile_population AS score, geom 
    FROM heatmap_population_api(%(scenario_id_input)s,%(modus_input)s);''',
    {"scenario_id_input": scenario_id_input,"modus_input": modus_input})    
    return db.select(sql_geojson)[0][0]

#with open('somefile.geojson', 'a') as f:
  #  f.write(heatmap_population(0,'default'))



def recompute_heatmap(scenario_id):
    """Function to recompute heatmap when network is changed."""
    
    if scenario_id == '0':
        return 'No scenario existing.'

    status_precomputed = db.select('''SELECT ways_heatmap_computed 
                FROM scenarios 
                WHERE scenario_id = %(scenario_id)s''', {"scenario_id": scenario_id})[0][0]

    if status_precomputed == True:
        return 'Scenario was already precomputed.'

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

    gridids = db.select("""SELECT UNNEST(gridids) FROM changed_grids""")

    for g in gridids:
        db.perform("""SELECT compute_area_isochrone(%(grid_id)s,%(scenario_id)s)""", {
                "grid_id": g[0], "scenario_id": scenario_id})

    buffer_geom = db.select("""SELECT ST_AsText(ST_BUFFER(ST_UNION(geom),0.0014)) 
    FROM area_isochrones_scenario 
    WHERE scenario_id = %(scenario_id)s""", {"scenario_id": scenario_id})

    buffer_geom = buffer_geom[0][0]
    db.perform("""DELETE FROM reached_pois_heatmap r
    USING pois_userinput p
    WHERE ST_Intersects(p.geom,ST_SETSRID(ST_GeomFromText(%(buffer_geom)s), 4326))
    AND r.gid = p.gid
    AND r.scenario_id = %(scenario_id)s;""", {"buffer_geom": buffer_geom, "scenario_id": scenario_id})
    
    db.perform('''SELECT reached_pois_heatmap(ST_SETSRID(ST_GeomFromText(%(buffer_geom)s), 4326), 0.0014, 'scenario', %(scenario_id)s);''',{"buffer_geom": buffer_geom, "scenario_id": scenario_id})
    
    db.perform('''UPDATE scenarios 
                SET ways_heatmap_computed = TRUE 
                WHERE scenario_id = %(scenario_id)s''', {"scenario_id": scenario_id})

    return