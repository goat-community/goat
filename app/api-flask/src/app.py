import io
import os


from flask import Flask, request, send_file, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from utils import response
from utils.async_function import *

from resources.recompute_heatmap import heatmap_connectivity, heatmap_population
from utils.geo.mvt import MVT
from db.db import Database
import config

from functools import wraps
import asyncio
import json
from geojson import dump
import zipfile
from io import StringIO

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
            self.record = db.fetch_one(
            f"""SELECT {
                translation_layers[body.get('table_name')]
            } AS deleted_feature_ids FROM scenarios WHERE scenario_id = {body.get('scenario_id')}::bigint"""
            )
            records = self.record
            return records
        elif mode == "update_deleted_features" :
            #sample body: {"mode":"update_deleted_features","deleted_feature_ids":[8,3,4],"table_name":"pois" ,"scenario_id":"2"} */

            db.perform(
            f"""UPDATE scenarios SET {translation_layers[body.get('table_name')]} = array{body.get('deleted_feature_ids')}::bigint[] WHERE scenario_id = {body.get('scenario_id')}::bigint""")
            return{
                "update_succes":True
            }
        elif mode == "delete_feature" :
            #delete is used to delete the feature from modified table if the user has drawn that feature by himself
            #sample body: {"mode":"delete_feature","table_name":"pois","scenario_id":"8","deleted_feature_ids":[2,3,4],"drawned_fid":"14"} */
            db.perform(
            f"""DELETE FROM {body.get('table_name')}_modified WHERE scenario_id = {body.get('scenario_id')}::bigint AND original_id = ANY((array{body.get('deleted_feature_ids')}))
            """)
            db.perform(
            f"""DELETE FROM {body.get('table_name')}_modified WHERE gid=({body.get('drawned_fid')});"""
            )
            return{
                'delete_success':True
                    }
        elif mode == "insert" :
        #/*sample body: {mode:"insert","userid":1,"scenario_name":"scenario1"}*/
            record = db.perform_with_result(f"""
            INSERT INTO scenarios (userid, scenario_name) VALUES ({body.get('userid')},'{body.get('scenario_name')}') RETURNING scenario_id
            """)
            return {
                "scenario_id":f"{record}"
                    }
        elif mode == "delete": 
        #/*sample body: {mode:"delete","scenario_id":97}*/
            db.perform(
            f"""DELETE FROM scenarios WHERE scenario_id = {body.get('scenario_id')}::bigint"""
            )
            return{
                "delete_success":True
            }
        elif mode == "update_scenario" :
        #/*sample body: {mode:"update_scenario","scenario_id":2,"scenario_name":"new_name2"}*/
            db.perform(
        f"""UPDATE scenarios SET scenario_name = '{body.get('scenario_name')}' WHERE scenario_id = {body.get('scenario_id')}::bigint
        """
        )
            return{
                "update_success":True
            }

class Isochrone(Resource):
    def post(self):
        body=request.get_json()
        requiredParams = [
            "user_id",
            "scenario_id",
            "minutes",
            "x",
            "y",
            "n",
            "speed",
            "concavity",
            "modus",
            "routing_profile"
        ]
        queryValues = []
        for key in  requiredParams :
            value = body[key]
            if key not in body.keys(): 
                print('key error')
                return 'key error'
            queryValues.append(value)
        
        query=f"""SELECT jsonb_build_object(
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
	    FROM (SELECT * FROM isochrones_api ({queryValues[0]},{queryValues[1]},{queryValues[2]},{queryValues[3]},{queryValues[4]},{queryValues[5]},{queryValues[6]},'{queryValues[7]}','{queryValues[8]}','{queryValues[9]}',NULL,NULL,NULL)) inputs) features;"""
        
        result=db.fetch_one(query)
        return result

class ManageUser(Resource):
    def post(self):
        body=request.get_json()
        mode=body.get('mode')
        if mode == "insert":
            #/*sample body: {"mode":"insert"}*/
            record = db.perform_with_result("INSERT INTO user_data (username, pw) VALUES ('','') RETURNING userid")
            return {
                    'userid':f'{record}'
                    }
        elif mode == "delete":
            #/*sample body: {"mode":"delete", "userid":1}*/
                db.perform(f"""DELETE FROM user_data WHERE userid = {body.get('userid')}::bigint""")
                return{
                    'delete_success':True
                }

class PingPONG(Resource):
    def get(self):
        return "pong"

class ExportScenario(Resource):       
    def post(self):
        body=request.get_json() 
        dicts=db.fetch_one(f"""SELECT * FROM export_changeset_scenario({body.get('scenario_id')})""")
        file_buffer = StringIO()
        my_zip = zipfile.ZipFile('scenarios.zip','w')
        for key in dicts.keys():
            with open(f'{key}.geojson', 'w') as f:
                dump(dicts[key], f)
            my_zip.write(f'{key}.geojson')
            os.remove(f'{key}.geojson')
        my_zip.close()
        file_buffer.seek(0)
        return Response(
        file_buffer,
        mimetype="application/zip",
        headers={"Content-disposition":
                    "attachment; filename=scenarios.zip"})

class ImportScenario(Resource):
    def post(self):
        body=request.get_json()
        payload =  json.dumps(body.get('payload'), separators=(',', ':'))
        result=db.fetch_one(f"SELECT import_changeset_scenario({body.get('scenario_id')}, {body.get('user_id')},jsonb_build_object('{body.get('layerName')}','{payload}'::jsonb))")
        return result

class PoisMultiIsochrones(Resource):
    def post(self):
        body=request.get_json() 
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
        queryValues = []
        for key in requiredParams :
            value = body[key]
            if not value :
                return {"success" :False , "error":"An error happened"}
            queryValues.append(value)

        #// Make sure to set the correct content type
        sqlQuery = f"""SELECT jsonb_build_object(
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
        FROM (SELECT * FROM multi_isochrones_api({queryValues[0]},{queryValues[1]},{queryValues[2]},{queryValues[3]},{queryValues[4]},{queryValues[5]},{queryValues[6]},{queryValues[7]},{queryValues[8]},ARRAY[{queryValues[9]}],ARRAY[{queryValues[10]}])) inputs) features;"""
        result=db.fetch_one(sqlQuery)
        return result

class CountPoisMultiIsochrones(Resource):
    def post(self):
        body=request.get_json()
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
        queryValues = []
        for key in requiredParams :
            value = body[key]

            if not value :
                return {"success" :False , "error":"An error happened"}
            queryValues.append(value)
        # // Make sure to set the correct content type
        sqlQuery = f"""SELECT jsonb_build_object(
        'type',       'Feature',
        'geometry',   ST_AsGeoJSON(geom)::jsonb,
        'properties', to_jsonb(inputs) - 'geom'
    ) AS feature 
    FROM (SELECT count_pois,region_name, geom FROM count_pois_multi_isochrones({queryValues[0]},{queryValues[1]},{queryValues[2]},{queryValues[3]},{queryValues[4]},{queryValues[5]},'{queryValues[6]}',array[{queryValues[7]}])) inputs;"""
        record = db.fetch_one(sqlQuery)
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
        func_varnames = list(globals()[heatmap_type].__code__.co_varnames)

        if sorted(request_args_keys) != sorted(func_varnames):
            return response.failure({
                'errors': {
                    'message': "Not all arguments available. "
                }
        })
        else:
            func_args = prepare_func_args(request_args, func_varnames)
            result = globals()[heatmap_type](*func_args)

        return result

api.add_resource(Heatmap,'/v2/map/heatmap/<string:heatmap_type>')

api.add_resource(Layer,'/v2/map/<string:layer>/<int:z>/<int:x>/<int:y>')

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
