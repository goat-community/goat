import io
import os
import inspect


from flask import Flask, request, send_file,Response, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from utils import response
from utils.async_function import *

from resources.recompute_heatmap import heatmap_connectivity, heatmap_population, heatmap_gravity, heatmap_luptai
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

import psycopg2
from psycopg2 import sql

db = Database()
app = Flask(__name__)
app.config.from_object(config.object_name[app.config['ENV']])
cors = CORS(app, resources={r"/v2/*": {"origins": "*"}})
api = Api(app)
PORT = os.getenv('APP_PORT', default=app.config['PORT'])

custom_methods_metadata = {
    'heatmap_gravity': {
        'methodToCall': 'recomputed_heatmap',
        'methodArgs': ["scenario_id"]
    }
}


def check_args_complete(request_args, query_values):
    request_args_keys = list(request_args.keys())

    if sorted(request_args_keys) != sorted(query_values):
        return response.failure({
            'errors': {
                'message': "Not all arguments available. "
            }
    })
    else:
        return request_args 


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
            records = db.select_with_identifiers('''SELECT {} AS deleted_feature_ids 
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
                {"userid": body.get('userid'), "scenario_name": body.get('scenario_name')})[0][0]
            return {
                "scenario_id":f"{scenario_id}"
                }
        elif mode == "delete": 
            #/*sample body: {mode:"delete","scenario_id":97}*/
            db.perform("""DELETE FROM scenarios WHERE scenario_id = %(scenario_id)s::bigint""",{"scenario_id": body.get('scenario_id')})
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
        
        requiredParams = ["user_id","scenario_id","minutes","x","y","n","speed","concavity","modus","routing_profile"]
        
        args = check_args_complete(args, requiredParams)
      
        query="""SELECT jsonb_build_object(
		'type',     'FeatureCollection',
		'features', jsonb_agg(features.feature)
        )
        FROM (
        SELECT jsonb_build_object(
		'type',       'Feature',
		'id',         gid,
		'geometry',   ST_AsGeoJSON(geom)::jsonb,
		'properties', to_jsonb(inputs) - 'gid' - 'geom'
        ) AS feature 
	    FROM (
                SELECT * 
                FROM isochrones_api (%(user_id)s,%(scenario_id)s,%(minutes)s,%(x)s,%(y)s,%(n)s,%(speed)s,%(concavity)s,%(modus)s,%(routing_profile)s,NULL,NULL,NULL)
            ) inputs
        ) features;"""
        
        result=db.select(query, 
        {
            "user_id": args["user_id"],"scenario_id": args["scenario_id"],"minutes": args["minutes"], "x": args["x"],"y": args["y"],"n": args["n"],
            "speed": args["speed"], "concavity": args["concavity"],"modus": args["modus"],"routing_profile": args["routing_profile"]
            }
        )[0][0]
 
        return result

class ManageUser(Resource):
    def post(self):
        body=request.get_json()
        print(body)
        mode=body.get('mode')
        if mode == "insert":
            #/*sample body: {"mode":"insert"}*/
            userid = db.select("INSERT INTO user_data (username, pw) VALUES ('','') RETURNING userid")[0][0]
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
        dicts=db.select('SELECT * FROM export_changeset_scenario(%(scenario_id)s)', {"scenario_id": body.get('scenario_id')})[0][0]
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
        , {"scenario_id": body.get('scenario_id'),"user_id":body.get('user_id'),"layerName":body.get('layerName'),"payload":payload})
        return result

class PoisMultiIsochrones(Resource):
    def post(self):
        args=request.get_json() 
        requiredParams = [
        "user_id",
        "scenario_id",
        "minutes",
        "speed",
        "n",
        "routing_profile",
        "alphashape_parameter",
        "modus",
        "region_type",
        "region",
        "amenities"
        ]

        args = check_args_complete(args, requiredParams)
        #// Make sure to set the correct content type
        sqlQuery = """SELECT jsonb_build_object(
        'type',     'FeatureCollection',
        'features', jsonb_agg(features.feature)
        )
        FROM (
        SELECT jsonb_build_object(
        'type',       'Feature',
        'id',         gid,
        'geometry',   ST_AsGeoJSON(geom)::jsonb,
        'properties', to_jsonb(inputs) - 'gid' - 'geom'
        ) AS feature 
        FROM (SELECT * FROM multi_isochrones_api(%(user_id)s,%(scenario_id)s,%(minutes)s,%(speed)s,%(n)s,%(routing_profile)s,%(alphashape_parameter)s,%(modus)s,%(region_type)s,ARRAY[%(region)s],ARRAY[%(amenities)s])) inputs) features;"""
        result=db.select(sqlQuery,
            {
            "user_id": args["user_id"],"scenario_id": args["scenario_id"],"minutes": args["minutes"], "speed": args["speed"],"n": args["n"],"routing_profile": args["routing_profile"],
            "alphashape_parameter": args["alphashape_parameter"], "modus": args["modus"],"region_type": args["region_type"],"region": args["region"],"amenities": args["amenities"]
            }
        )
        return result
        
class CountPoisMultiIsochrones(Resource):
    def post(self):
        args=request.get_json()
        requiredParams = [
        "user_id",
        "scenario_id",
        "modus",
        "minutes",
        "speed",
        "region_type",
        "region",
        "amenities"
        ]
        args = check_args_complete(args, requiredParams)
        # // Make sure to set the correct content type
        sqlQuery = """SELECT jsonb_build_object(
        'type',       'Feature',
        'geometry',   ST_AsGeoJSON(geom)::jsonb,
        'properties', to_jsonb(inputs) - 'geom'
    ) AS feature 
    FROM (SELECT count_pois,region_name, geom FROM count_pois_multi_isochrones(%(user_id)s,%(scenario_id)s,%(modus)s,%(minutes)s,%(speed)s,%(region_type)s,%(region)s,array[%(amenities)s])) inputs;"""
        record = db.select(sqlQuery,
            {
            "user_id": args["user_id"],"scenario_id": args["scenario_id"],"modus": args["modus"],"minutes": args["minutes"], "speed": args["speed"],
            "region_type": args["region_type"],"region": args["region"],"amenities": args["amenities"]
            }
        )[0][0]
        return record

class UploadAllScenariosResource(Resource):
    @async_action
    async def post(self):
        body=request.get_json()
        scenarioId = body.get('scenario_id')
        task1 = asyncio.create_task(fun_task1(db,scenarioId))
        task2 = asyncio.create_task(fun_task2(db,scenarioId))
        await task1
        await task2
        self.network_modification_record= fun_task1(db,scenarioId)
        network_modification = self.network_modification_record
        return {
                'population_modification':network_modification
        }

class DeleteAllScenarioData(Resource):
    @async_action
    async def post(self):
        body=request.get_json()
        scenarioId = body.get('scenario_id')
        task1 = asyncio.create_task(delete_task(db,scenarioId))
        task2 = asyncio.create_task(select_task(db,scenarioId))
        await task1
        await task2
        population_modification_record=cur.fetchall()
        return {'network_modification':network_modification_record,
                'population_modification':population_modification_record
        }

class LayerController(Resource):
    def post(self):
        body=request.get_json()
        mode=body.get('mode')
        table_name = body.get('table_name') + '_modified'
        if mode == "read":
            #{"mode":"read","table_name":"pois","scenario_id":"2"}
            prepared_query = '''SELECT * FROM {} WHERE scenario_id = %(scenario_id)s::bigint'''

            records = db.select_with_identifiers(
                prepared_query, identifiers=[table_name], params={"scenario_id": body.get('scenario_id')}, return_type='geojson'
            )

            return records
        if mode == "insert":
            #{"mode":"insert","table_name":"pois","scenario_id":"1","name":"Test","geom":"POINT(11.4543 48.1232)",amenity:'club'}

            dfs = gpd.GeoDataFrame()
            for f in body['features']:
                columns = list(f.keys())
                if 'geom' in f.keys():
                    raw_query = "INSERT INTO {}({}, geom) VALUES ({}, ST_SETSRID(ST_GEOMFROMTEXT(%(geom)s), 4326)) RETURNING {}, geom"
                    columns.remove('geom')
                else:
                    raw_query = "INSERT INTO ({}) VALUES ({}) RETURNING {}"

                prepared_query = sql.SQL(raw_query).format(
                    sql.Identifier(table_name),
                    sql.SQL(', ').join(map(sql.Identifier, columns)),
                    sql.SQL(', ').join(map(sql.Placeholder, columns)),
                    sql.SQL(', ').join(map(sql.Identifier, columns))
                )   

                df = db.select_with_identifiers(prepared_query, params=f, return_type='geodataframe')

                if dfs.empty: 
                    dfs = df 
                else:
                    dfs = dfs.append(df)
            return json.loads(dfs.to_json())
            
        if mode == "update":
            #{"mode":"update","table_name":"pois","scenario_id":"8","gid":"1","name":"Test","geom":"POINT(11.4543 48.1232)"}
            for f in body['features']:
                columns = list(f.keys())

                if 'geom' in f.keys():
                    raw_query = "UPDATE {} SET geom=ST_SETSRID(ST_GEOMFROMTEXT(%(geom)s), 4326), {}={},"
                    columns.remove('geom')
                else:
                    raw_query = "UPDATE {} SET {}={},"

                where_condition = sql.SQL("WHERE scenario_id = %(scenario_id)s AND gid = %(gid)s")

                columns_sql = []
                for i in columns[1:]:      
                    columns_sql.append(sql.SQL('{}={}').format(sql.Identifier(i), sql.Placeholder(i)))
                
                columns_sql = sql.SQL(', ').join(columns_sql)

                update_sql = [
                    sql.SQL(raw_query).format(sql.Identifier(table_name),sql.Identifier(columns[0]),sql.Placeholder(columns[0])),
                    columns_sql,
                    where_condition
                ] 
                sql_update = sql.SQL(' ').join(update_sql)
                db.perform(sql_update, f)

            return{
                "update_success": True
                }

        if mode == "delete":
            #{"mode":"delete","table_name":"pois","gid": "26","scenario_id":"4"}
            for f in body['features']:
                db.perform_with_identifiers("DELETE FROM {} WHERE gid = %(gid)s and scenario_id = %(scenario_id)s", 
                [table_name], {"gid":f["gid"],"scenario_id": f["scenario_id"]})
            
            return{
                "delete_success": True
                }


class Layer(Resource):
    def __init__(self):
        self.metadata = db.select('''SELECT * FROM layer_metadata''')[0][0]
        self.mvt = MVT()
        # Attach the custom logic method names and argumets to the existing metada
        for attr, value in custom_methods_metadata.items():
            if (attr in self.metadata):
                self.metadata[attr].update(value)

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
        # Find table/function name. If there is a custom python logic to be executed before,
        # we should run it first. A metadata object will contain methodToCall and methodArgs
        # needed for the method call.
        request_args = request.args.to_dict()
        if ('methodToCall' in layer_config):
            method_args = []
            for index, method_arg in enumerate(layer_config['methodArgs']):
                if not method_arg in request_args:
                    method_args = []
                    break
                method_args.append(request_args[method_arg])
            print(method_args)
            if len(method_args) > 0:
                recompute_heatmap(*method_args)

        table = layer
        if layer_config['layer_type'] == "function" and layer_config['args'] is not None:
            args = ""
            for index, arg in enumerate(layer_config['args']):
                if not arg in request_args:
                    return response.failure({
                        'errors': {
                            'message': "Not all arguments available. "
                        }
                    })
                if index < len(layer_config['args']) - 1:
                    args += request_args[arg] + ","
                else:
                    args += request_args[arg]
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
        bytes = io.BytesIO(pbf)
        return send_file(bytes, mimetype='application/vnd.mapbox-vector-tile')


def prepare_func_args(request_args, func_varnames):
    func_args = []
    for i in func_varnames:
        func_args.append(request_args[i].replace("'",""))
    
    return func_args


class Heatmap(Resource):
    def get(self, heatmap_type):
        request_args = request.args.to_dict()
        request_args_keys = list(request_args.keys())
        request_val = list(request_args.values())
        func_varnames = inspect.getargspec(globals()[heatmap_type]).args

        check_args_complete(request_args, func_varnames)

        func_args = prepare_func_args(request_args, func_varnames)
        result = globals()[heatmap_type](*func_args)

        return result

api.add_resource(Heatmap,'/v2/map/heatmap/<string:heatmap_type>')

api.add_resource(Layer,'/v2/map/<string:layer>/<int:z>/<int:x>/<int:y>')

api.add_resource(LayerController,'/api/layer_controller')

api.add_resource(CountPoisMultiIsochrones,'/api/count_pois_multi_isochrones')

api.add_resource(PoisMultiIsochrones,'/api/pois_multi_isochrones')

api.add_resource(ImportScenario,'/api/import_scenario')

api.add_resource(ExportScenario,'/api/export_scenario')

api.add_resource(PingPONG,'/ping')
            
api.add_resource(ManageUser,'/api/userdata')

api.add_resource(Isochrone,'/api/isochrone')

api.add_resource(Scenarios, '/api/scenarios')

api.add_resource(DeleteAllScenarioData,'/api/deleteAllScenarioData')

api.add_resource(UploadAllScenariosResource,'/api/upload_all_scenarios')


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
