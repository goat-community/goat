import io
import os
import inspect


from flask import Flask, request, send_file, Response, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from utils import response
from utils.async_function import *

from resources.heatmap import heatmap_connectivity, heatmap_population, heatmap_gravity, heatmap_luptai
from utils.geo.mvt import MVT
from db.db import Database
import config

from functools import wraps
import asyncio
import json
from geojson import dump
import tempfile
import geojson
import zipstream
import geopandas as gpd
import geobuf


import psycopg2
from psycopg2 import sql

db = Database()
app = Flask(__name__)
app.config.from_object(config.object_name[app.config['ENV']])
cors = CORS(app, resources={r"/v2/*": {"origins": "*"}})
api = Api(app)
PORT = os.getenv('APP_PORT', default=app.config['PORT'])


def check_args_complete(body, query_values):
    body_keys = list(body.keys())

    if sorted(body_keys) != sorted(query_values):
        return response.failure({
            'errors': {
                'message': "Not all arguments available. "
            }
    })
    else:
        return body 

def async_action(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

class Scenarios(Resource):
    def post(self):
        body=request.get_json()
        mode=body.get('mode')
        translation_layers = {
            "ways": "deleted_ways",
            "pois": "deleted_pois",
            "buildings": "deleted_buildings"
            }
        if mode == "read_deleted_features" :
            #sample body: {"mode":"read_deleted_features","table_name":"pois" ,"scenario_id":"1"} 
            records = db.select('''SELECT {} AS deleted_feature_ids 
            FROM scenarios 
            WHERE scenario_id = %(scenario_id)s::bigint''', 
            [translation_layers[body.get('table_name')]], {"scenario_id": body.get('scenario_id')})
      
            return records
        elif mode == "update_deleted_features" :
            #sample body: {"mode":"update_deleted_features","deleted_feature_ids":[8,3,4],"table_name":"pois" ,"scenario_id":"2"} */
            deleted_features_ids = body.get('deleted_feature_ids')
            
            db.perform_with_identifiers("""UPDATE scenarios 
            SET {} = %(deleted_feature_ids)s::bigint[] 
            WHERE scenario_id = %(scenario_id)s::bigint""", 
            [translation_layers[body.get('table_name')]], {"scenario_id": body.get('scenario_id'), "deleted_feature_ids": body.get('deleted_feature_ids')})
            
            return{
                "update_succes":True
            }
        elif mode == "delete_feature" :
            #delete is used to delete the feature from modified table if the user has drawn that feature by himself
            #sample body: {"mode":"delete_feature","table_name":"pois","scenario_id":"8","deleted_feature_ids":[2,3,4],"drawned_fid":"14"} */
            table_name = body.get('table_name') + '_modified' 

            db.perform_with_identifiers("""DELETE FROM {}
            WHERE scenario_id = %(scenario_id)s::bigint 
            AND original_id = ANY((%(deleted_feature_ids)s))""", 
            [table_name], {"scenario_id": body.get('scenario_id'), "deleted_feature_ids": body.get('deleted_feature_ids')})
            
            db.perform_with_identifiers("DELETE FROM {} WHERE gid=%(gid)s", [table_name], {"gid": body.get('drawned_fid')})

            return{
                'delete_success':True
            }
        elif mode == "insert" :
            #/*sample body: {mode:"insert","userid":1,"scenario_name":"scenario1"}*/
            scenario_id = db.select("""INSERT INTO scenarios (userid, scenario_name) VALUES (%(userid)s,%(scenario_name)s) RETURNING scenario_id""", 
                params={"userid": body.get('userid'), "scenario_name": body.get('scenario_name')}, return_type='raw')[0][0]
            return {
                "scenario_id":f"{scenario_id}"
                }
        elif mode == "delete": 
            #/*sample body: {mode:"delete","scenario_id":97}*/
            db.perform("""DELETE FROM scenarios WHERE scenario_id = %(scenario_id)s""",{"scenario_id": body.get('scenario_id')})
            return{
                "delete_success":True
            }
        elif mode == "update_scenario" :
            #/*sample body: {mode:"update_scenario","scenario_id":2,"scenario_name":"new_name2"}*/
            db.perform("""UPDATE scenarios SET scenario_name = %(scenario_name)s 
            WHERE scenario_id = %(scenario_id)s::bigint""", {"scenario_name": body.get('scenario_name'), "scenario_id": body.get('scenario_id')})
            return{
                "update_success":True
            }

class Isochrone(Resource):
    def post(self):
        args=request.get_json()
        
        if 'return_type' in args: 
            return_type = args['return_type']
            del args['return_type']

        if 'objectid' in args and return_type == "shapefile":
            prepared_query = '''SELECT gid, objectid, step, modus, parent_id, population, sum_pois::text, geom 
            FROM isochrones WHERE objectid = %(objectid)s'''
            result = db.select(prepared_query, params={"objectid": args["objectid"]}, return_type='shapefile')
            result = Response(result, mimetype='application/zip')
            result.headers['Content-Disposition'] = 'attachment; filename={}'.format('isochrones.zip')
            return result

        requiredParams = ["user_id","scenario_id","minutes","x","y","n","speed","concavity","modus","routing_profile"]
        args = check_args_complete(args, requiredParams)
            
        prepared_query = """SELECT gid, objectid, coordinates, ST_ASTEXT(ST_MAKEPOINT(coordinates[1], coordinates[2])) AS starting_point,
        step, speed::integer, modus, parent_id, sum_pois, geom 
        FROM isochrones_api(%(user_id)s,%(scenario_id)s,%(minutes)s,%(x)s,%(y)s,%(n)s,%(speed)s,%(concavity)s,%(modus)s,%(routing_profile)s,NULL,NULL,NULL)"""
        
        args_vals =  {
            "user_id": args["user_id"],"scenario_id": args["scenario_id"],"minutes": args["minutes"], "x": args["x"],"y": args["y"],"n": args["n"],
            "speed": args["speed"], "concavity": args["concavity"],"modus": args["modus"],"routing_profile": args["routing_profile"]
        }
        record = db.select(prepared_query, params=args_vals, return_type='geojson')

        return record[0][0]

class PoisMultiIsochrones(Resource):
    def post(self):
        args=request.get_json() 

        if 'return_type' in args: 
            return_type = args['return_type']
            del args['return_type']

        if 'objectid' in args and return_type == "shapefile":
            prepared_query = '''SELECT gid, userid, step, speed, modus, parent_id, routing_profile, population::TEXT, geom 
            FROM multi_isochrones 
            WHERE objectid = %(objectid)s'''
            result = db.select(prepared_query, params={"objectid": args["objectid"]}, return_type='shapefile')
            result = Response(result, mimetype='application/zip')
            result.headers['Content-Disposition'] = 'attachment; filename={}'.format('isochrones.zip')
            return result

        requiredParams = ["user_id","scenario_id","minutes","speed","n","routing_profile","alphashape_parameter","modus","region_type","region","amenities"]

        args = check_args_complete(args, requiredParams)
        #// Make sure to set the correct content type
   
        prepared_query = """SELECT *
        FROM multi_isochrones_api(%(user_id)s,%(scenario_id)s,%(minutes)s,%(speed)s,%(n)s,%(routing_profile)s,%(alphashape_parameter)s,%(modus)s,%(region_type)s,%(region)s,%(amenities)s)"""
        
        args_vals =  {
            "user_id": args["user_id"],"scenario_id": args["scenario_id"],"minutes": args["minutes"], "speed": args["speed"],"n": args["n"],"routing_profile": args["routing_profile"],
            "alphashape_parameter": args["alphashape_parameter"], "modus": args["modus"],"region_type": args["region_type"],"region": args["region"],"amenities": args["amenities"]
        }

        record = db.select(prepared_query, params=args_vals, return_type='geojson')
    
        return record[0][0]
        
class CountPoisMultiIsochrones(Resource):
    def post(self):
        args=request.get_json()
        requiredParams = ["user_id","scenario_id","modus","minutes","speed","region_type","region","amenities"]
        args = check_args_complete(args, requiredParams)
        # // Make sure to set the correct content type

        prepared_query = """SELECT row_number() over() AS gid, count_pois, region_name, geom 
        FROM count_pois_multi_isochrones(%(user_id)s,%(scenario_id)s,%(modus)s,%(minutes)s,%(speed)s,%(region_type)s,%(region)s,array[%(amenities)s])"""
        
        args_vals = {
            "user_id": args["user_id"],"scenario_id": args["scenario_id"],"modus": args["modus"],"minutes": args["minutes"],
             "speed": args["speed"],"region_type": args["region_type"],"region": args["region"],"amenities": args["amenities"]
        }

        record = db.select(prepared_query, params=args_vals, return_type='geojson')
        
        return record[0][0]




class ManageUser(Resource):
    def post(self):
        body=request.get_json()
        print(body)
        mode=body.get('mode')
        if mode == "insert":
            #/*sample body: {"mode":"insert"}*/
            userid = db.select("INSERT INTO user_data (username, pw) VALUES ('','') RETURNING userid", return_type='raw')[0][0]
            return {
                    'userid':f'{userid}'
                }
        elif mode == "delete":
            #/*sample body: {"mode":"delete", "userid":1}*/
                userid = mode=body.get('userid')
                db.perform("DELETE FROM user_data WHERE userid = %(userid)s::bigint", {"userid": userid})
                return{
                    'delete_success':True
                }

class PingPONG(Resource):
    def get(self):
        return "pong"

class ExportScenario(Resource):       
    def post(self):
        body=request.get_json() 
        dicts=db.select('SELECT * FROM export_changeset_scenario(%(scenario_id)s)', 
        params={"scenario_id": body.get('scenario_id')}, return_type='raw')[0][0]
        my_zip = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)
        for key in dicts.keys():
            tmp_file = tempfile.mkstemp(prefix=f"{key}",suffix='.geojson')
            
            with open(tmp_file[1], 'w') as f:
                geojson.dump(dicts[key],f)
            my_zip.write(f.name,arcname= f"{key}.geojson")
        response = Response(my_zip, mimetype='application/zip')
        response.headers['Content-Disposition'] = 'attachment; filename={}'.format('files.zip')
        return response

class ImportScenario(Resource):
    def post(self):
        body=request.get_json()
        payload =  json.dumps(body.get('payload'), separators=(',', ':'))
        result=db.select("SELECT import_changeset_scenario(%(scenario_id)s, %(user_id)s,jsonb_build_object(%(layerName)s,%(payload)s::jsonb))"
        , params={"scenario_id": body.get('scenario_id'),"user_id":body.get('user_id'),"layerName":body.get('layerName'),"payload":payload}, return_type='raw')
        return result

class UploadAllScenariosResource(Resource):
    def post(self):
        body = request.get_json()
        scenario_id = body.get('scenario_id')
        
        db.perform('SELECT * FROM network_modification(%(scenario_id)s)', {"scenario_id": scenario_id})
        db.perform('SELECT * FROM population_modification(%(scenario_id)s)', {"scenario_id": scenario_id})
        
        return {
            "response": "Scenarios are reflected."
        }

class DeleteAllScenarioData(Resource):
    def post(self):
        body = request.get_json()
        scenario_id = body.get('scenario_id')
        db.perform('DELETE FROM scenarios WHERE scenario_id = %(scenario_id)s', {"scenario_id": scenario_id})
        db.perform('SELECT network_modification(%(scenario_id)s)', {"scenario_id": scenario_id})

        return {
            "response": "All changes are reverted."
        }
   
class OsmTimestamp(Resource):
    def get(self):
        result = db.select(
        "SELECT split_part(variable_simple,'T',1) FROM variable_container vc WHERE identifier = 'data_recency'", 
        return_type='raw')[0][0]

        return {
            "osm_timestamp" : result 
        }
class LayerSchema(Resource):
    def get(self, table_name):
        result = db.select('''SELECT jsonb_agg(jsonb_build_object('column_name', column_name, 'data_type', data_type, 'is_nullable', is_nullable))
        FROM information_schema.columns
        WHERE table_name = %(table_name)s''', params={"table_name": table_name}, return_type='raw')[0][0]

        return result 

class LayerRead(Resource):
    def post(self):
     
        body = request.get_json()
        table_name = body.get('table_name') 
        return_type = body.get('return_type') 

        if table_name == 'pois' and "geom" not in body:
            prepared_query = '''SELECT * FROM pois_visualization(%(scenario_id)s,%(amenities)s,%(routing_profile)s,%(modus)s)'''
        elif table_name == 'aois':
            prepared_query = '''SELECT gid, a.amenity, a.name, a.geom
            FROM aois a
            WHERE a.amenity IN(SELECT UNNEST(%(amenities)s))'''
        elif table_name == 'edges':
            prepared_query = '''SELECT id AS gid, %(modus_input)s AS modus, cost, geom
            FROM edges 
            WHERE objectid = %(objectid)s'''
        elif table_name == 'pois':
            prepared_query = '''SELECT * FROM pois_visualization(%(scenario_id)s,%(amenities)s,%(routing_profile)s,%(modus)s) 
            WHERE ST_Intersects(geom, ST_SETSRID(ST_GEOMFROMTEXT(%(geom)s), 4326))'''
        elif table_name == 'mapping_pois_opening_hours':
            prepared_query = '''SELECT osm_id, amenity, amenity || '_accessible' as amenity_icon, name, 
            CASE WHEN origin_geometry = 'point' THEN 'node' ELSE 'way' END as osm_type, geom
            FROM pois_mapping
            WHERE opening_hours IS NULL
            AND amenity IN (SELECT UNNEST(%(amenities)s))'''
        elif table_name == 'ways':
            prepared_query = '''SELECT id as gid, * FROM ways
            WHERE ST_Intersects(geom, ST_SETSRID(ST_GEOMFROMTEXT(%(geom)s), 4326))
            AND class_id NOT IN (0,101,102,103,104,105,106,107,501,502,503,504,701,801)'''
        elif table_name == 'buildings': 
            prepared_query = '''SELECT * FROM buildings
            WHERE ST_Intersects(geom, ST_SETSRID(ST_GEOMFROMTEXT(%(geom)s), 4326))'''
        elif table_name == 'study_area_crop':
            prepared_query = '''SELECT * FROM study_area_crop'''
        elif table_name == 'study_area_union':
            prepared_query = '''SELECT * FROM study_area_union'''
        elif table_name == 'study_area':
            prepared_query = '''SELECT * FROM study_area'''
        elif table_name == 'modeshare':
            prepared_query = '''SELECT * FROM modeshare'''

        else:
            return {
                "Error": "No valid table was selected."
            }

        _body = body.copy()
        # Workaround to avoid the the accuracy lose coming from ST_AsGeobuf method bug. 
        if (return_type == 'geobuf'):
            sql_return_type = 'geojson'
            _body["return_type"] = 'geojson'
        else:
            sql_return_type = return_type

        result = db.select(prepared_query, params=_body, return_type=sql_return_type)
        if (return_type == 'geobuf'):
            result = geobuf.encode(result[0][0]);
        if body["return_type"] == 'geobuf':
            result_bytes = io.BytesIO(result)
            return send_file(result_bytes, mimetype='application/geobuf.pbf')
        else:
            return result  


class LayerController(Resource):
    def post(self):
        body=request.get_json()
        mode=body.get('mode')

        table_name = body.get('table_name') 

        if body.get('table_name') not in ["ways_modified","pois_modified","buildings_modified","population_modified"]:
            return {
                "Error": "No valid table was selected."
            }

        if mode == "read":
            prepared_query = '''SELECT * FROM {} WHERE scenario_id = %(scenario_id)s::bigint'''

            records = db.select(
                prepared_query, identifiers=[table_name], params={"scenario_id": body.get('scenario_id')}, return_type='geojson'
            )

            return records
        if mode == "insert":
            dfs = gpd.GeoDataFrame()
            for f in body['features']:
                columns = list(f.keys())
                if 'geom' in f.keys():
                    raw_query = "INSERT INTO {}({}, geom) VALUES ({}, ST_SETSRID(ST_GEOMFROMTEXT(%(geom)s), 4326)) RETURNING gid, {}, geom"
                    columns.remove('geom')
                else:
                    raw_query = "INSERT INTO ({}) VALUES ({}) RETURNING {}"

                prepared_query = sql.SQL(raw_query).format(
                    sql.Identifier(table_name),
                    sql.SQL(', ').join(map(sql.Identifier, columns)),
                    sql.SQL(', ').join(map(sql.Placeholder, columns)),
                    sql.SQL(', ').join(map(sql.Identifier, columns))
                )   

                df = db.select(prepared_query, params=f, return_type='geodataframe')

                if dfs.empty: 
                    dfs = df 
                else:
                    dfs = dfs.append(df)
            return json.loads(dfs.to_json())
            
        if mode == "update":
            dfs = gpd.GeoDataFrame()
            for f in body['features']:
                columns = list(f.keys())

                if 'geom' in f.keys():
                    raw_query = "UPDATE {} SET geom=ST_SETSRID(ST_GEOMFROMTEXT(%(geom)s), 4326), {}={},"
                    columns.remove('geom')
                else:
                    raw_query = "UPDATE {} SET {}={},"

                where_condition = sql.SQL("WHERE scenario_id = %(scenario_id)s AND gid = %(gid)s RETURNING geom,")

                columns_sql = []
                for i in columns[1:]:      
                    columns_sql.append(sql.SQL('{}={}').format(sql.Identifier(i), sql.Placeholder(i)))
                
                columns_sql = sql.SQL(', ').join(columns_sql)

                update_sql = [
                    sql.SQL(raw_query).format(sql.Identifier(table_name),sql.Identifier(columns[0]),sql.Placeholder(columns[0])),
                    columns_sql,
                    where_condition,
                    sql.SQL(', ').join(map(sql.Identifier, columns))
                ] 
                prepared_query = sql.SQL(' ').join(update_sql)

                df = db.select(prepared_query, params=f, return_type='geodataframe')

                if dfs.empty: 
                    dfs = df 
                else:
                    dfs = dfs.append(df)
            return json.loads(dfs.to_json())

        if mode == "delete":
            for f in body['features']:
                db.perform_with_identifiers("DELETE FROM {} WHERE gid = %(gid)s and scenario_id = %(scenario_id)s", 
                [table_name], {"gid":f["gid"],"scenario_id": f["scenario_id"]})
            
        return{
            "Response":  "Delete success"
            }


class Layer(Resource):
    def __init__(self):
        self.metadata = db.select('''SELECT * FROM layer_metadata''', return_type='raw')[0][0]
        self.mvt = MVT()
        
    def get(self, layer, z, x, y):
        tile = {
            'zoom': z,
            'x': x,
            'y': y,
            'format': "pbf",
        }
        layer_config = self.metadata[layer]
        # Check if layer exists in db
        if not layer_config:
            return response.failure({
                'errors': {
                    'message': "The layer doesn't exist"
                }
            }, 400)
        # Get the env for the tile.
        if not (tile and self.mvt.tileIsValid(tile)):
            return response.failure({
                'errors': {
                    'message': "invalid tile path: %s" % (self.path)
                }
            }, 400)

        env = self.mvt.tileToEnvelope(tile)

        # Find table/function name.
        body = request.args.to_dict()

        table = layer
        if layer_config['layer_type'] == "function" and layer_config['args'] is not None:
            args = ""
            for index, arg in enumerate(layer_config['args']):
                if not arg in body:
                    return response.failure({
                        'errors': {
                            'message': "Not all arguments available. "
                        }
                    })
                if index < len(layer_config['args']) - 1:
                    args += body[arg] + ","
                else:
                    args += body[arg]
            table = '''(SELECT * FROM {layer}({args}))'''.format(
                layer=layer, args=args)
        # Create the table object to pass in sql template string
        tbl = {
            'env': self.mvt.envelopeToBoundsSQL(env),
            'geomColumn': layer_config['geom'],
            'attrColumns': layer_config['columns'],
            'srid': layer_config['srid'],
            'table': table
        }
        # Create the sql string
        vtSql = self.mvt.toSQL(tbl)
        # Execute sql and send pbf back
        pbf = db.fetch_one(vtSql)
        result_bytes = io.BytesIO(pbf)
        return send_file(result_bytes, mimetype='application/vnd.mapbox-vector-tile')


class Heatmap(Resource):
    def post(self):

        body = request.get_json()
        body_keys = list(body.keys())
        request_val = list(body.values())

        heatmap_type = body.get('heatmap_type')

        del body['heatmap_type']

        func_varnames = inspect.getargspec(globals()[heatmap_type]).args

        check_args_complete(body, func_varnames)

        func_args = []
        for i in func_varnames:
            func_args.append(body[i])

        result = globals()[heatmap_type](*func_args)

        if body.get('return_type') == 'geobuf':
            result_bytes = io.BytesIO(result[0][0])
            return send_file(result_bytes, mimetype='application/geobuf.pbf')
        elif body.get('return_type') == 'shapefile':
            response = Response(result, mimetype='application/zip')
            response.headers['Content-Disposition'] = 'attachment; filename={}'.format('files.zip')
            return response
        else:
            return result  
   

api.add_resource(Heatmap,'/api/map/heatmap')

api.add_resource(Layer,'/api/map/layer/<string:layer>/<int:z>/<int:x>/<int:y>')

api.add_resource(LayerSchema,'/api/map/layer_schema/<string:table_name>')

api.add_resource(LayerRead,'/api/map/layer_read')

api.add_resource(LayerController,'/api/map/layer_controller')

api.add_resource(CountPoisMultiIsochrones,'/api/map/count_pois_multi_isochrones')

api.add_resource(PoisMultiIsochrones,'/api/map/pois_multi_isochrones')

api.add_resource(ImportScenario,'/api/map/import_scenario')

api.add_resource(ExportScenario,'/api/map/export_scenario')

api.add_resource(PingPONG,'/ping')
            
api.add_resource(ManageUser,'/api/userdata')

api.add_resource(OsmTimestamp,'/api/osm_timestamp')

api.add_resource(Isochrone,'/api/map/isochrone')

api.add_resource(Scenarios, '/api/map/scenarios')

api.add_resource(DeleteAllScenarioData,'/api/map/deleteAllScenarioData')

api.add_resource(UploadAllScenariosResource,'/api/map/upload_all_scenarios')


# SERVER CONFIG
if app.config['REMOTE_DEBUGGING']:
    import ptvsd
    ptvsd.enable_attach(
        address=('0.0.0.0', app.config['REMOTE_DEBUGGING_PORT']), redirect_output=True)
    ptvsd.wait_for_attach()
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
