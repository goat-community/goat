from db.db import Database
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import geojson
import geobuf
import json  
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

def recompute_heatmap(scenario_id):
    """Function to recompute heatmap when network is changed."""
    import datetime
    begin_time = datetime.datetime.now()


    if scenario_id == 0:
        return 'Scenario is 0 which stands for no scenario.'

    status_precomputed = db.select('''SELECT ways_heatmap_computed 
                FROM scenarios 
                WHERE scenario_id = %(scenario_id)s''', {"scenario_id": str(scenario_id)})

    if status_precomputed == []:
        return 'Scenario_id is not existing.'

    if status_precomputed[0][0] == True:
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

    #buffer_geom = db.select("""SELECT ST_AsText(ST_BUFFER(ST_UNION(geom),0.0014)) 
    #FROM area_isochrones_scenario 
    #WHERE scenario_id = %(scenario_id)s""", {"scenario_id": scenario_id})

    buffer_geom = db.select("""SELECT DISTINCT ST_AsText(ST_UNION(geom)) FROM changed_grids""")[0][0]

    #db.perform("""DELETE FROM reached_pois_heatmap r
    #USING pois_userinput p
    #WHERE ST_Intersects(p.geom,ST_SETSRID(ST_GeomFromText(%(buffer_geom)s), 4326))
    #AND r.gid = p.gid
    #AND r.scenario_id = %(scenario_id)s;""", {"buffer_geom": buffer_geom, "scenario_id": scenario_id})
    
    #db.perform('''SELECT reached_pois_heatmap(ST_SETSRID(ST_GeomFromText(%(buffer_geom)s), 4326), 0.0014, 'scenario', %(scenario_id)s);''',{"buffer_geom": buffer_geom, "scenario_id": scenario_id})
    
    db.perform('''UPDATE scenarios 
                SET ways_heatmap_computed = TRUE 
                WHERE scenario_id = %(scenario_id)s''', {"scenario_id": scenario_id})

    print('Successful calculated')
    print(datetime.datetime.now()-begin_time)
    return

def jsonb_to_geojson(jsonb_dict):
    json_string = json.loads(jsonb_dict)
    return json_string


def heatmap_gravity(pois, modus_input, scenario_id_input, return_type):
    recompute_heatmap(scenario_id_input)

    result = db.select_with_identifiers('''SELECT percentile_accessibility AS score, %(modus_input)s AS modus, geom 
        FROM heatmap_gravity(%(pois)s::jsonb,%(modus_input)s,%(scenario_id_input)s)''', 
        params = {"pois": pois, "modus_input": modus_input, "scenario_id_input": scenario_id_input}, return_type=return_type)

    return result


def heatmap_population(modus_input, scenario_id_input):
    db.perform('DROP TABLE IF EXISTS heatmap_temp;')

    db.perform('''CREATE TEMP TABLE heatmap_temp AS 
    SELECT percentile_population AS score,%(modus_input)s AS modus, geom 
    FROM heatmap_population_api(%(modus_input)s,%(scenario_id_input)s);''',
    {"scenario_id_input": scenario_id_input,"modus_input": modus_input})   

    return jsonb_to_geojson(db.select(sql_geojson)[0][0])

def heatmap_luptai(pois, modus_input, scenario_id_input):
    recompute_heatmap(scenario_id_input)
    db.perform('DROP TABLE IF EXISTS heatmap_temp;')

    db.perform('''CREATE TEMP TABLE heatmap_temp AS 
    SELECT population_accessibility AS score, %(modus_input)s AS modus, geom 
    FROM heatmap_luptai(%(pois)s::jsonb,%(modus_input)s,%(scenario_id_input)s);''',
    {"pois": pois, "modus_input": modus_input, "scenario_id_input": scenario_id_input})
    
    return jsonb_to_geojson(db.select(sql_geojson)[0][0])


def heatmap_connectivity(modus_input, scenario_id_input):
    recompute_heatmap(scenario_id_input)
    db.perform('DROP TABLE IF EXISTS heatmap_temp;')

    db.perform('''CREATE TEMP TABLE heatmap_temp AS 
    SELECT percentile_area_isochrone AS score, %(modus_input)s AS modus, geom
    FROM heatmap_connectivity(%(modus_input)s,%(scenario_id_input)s);''',
    {"scenario_id_input": scenario_id_input,"modus_input": modus_input})    
    return jsonb_to_geojson(db.select(sql_geojson)[0][0])


def convert_geobuf(layer_geojson):
    pbf = geobuf.encode(layer_geojson)
    return pbf



#x = heatmap_connectivity('default',0)
#convert_geobuf(heatmap_connectivity('default',0))

#with open('somefile.geojson', 'a') as f:
#    f.write(heatmap_connectivity('scenario',9))

