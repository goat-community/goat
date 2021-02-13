from flask import request,jsonify,Flask,Response
from functools import wraps
import asyncio
import json
import psycopg2
import os
from geojson import dump
import zipfile
from io import StringIO
from db_config import *


app = Flask(__name__)



@app.route("/api/scenarios", methods=["POST"])
def scenarios():
    body=request.get_json()
    mode=body.get('mode')
    translation_layers = {
        "ways": "deleted_ways",
        "pois": "deleted_pois",
        "buildings": "deleted_buildings"
        }
    try:
        con = psycopg2.connect("host={} dbname={} user={} password={} port = {}".format(host,db_name,db_user,db_password,port))
        cur=con.cursor()
        if mode == "read_deleted_features" :
            #sample body: {"mode":"read_deleted_features","table_name":"pois" ,"scenario_id":"1"} 
            cur.execute(
            f"""SELECT {
                translation_layers[body.get('table_name')]
            } AS deleted_feature_ids FROM scenarios WHERE scenario_id = {body.get('scenario_id')}::bigint"""
            )
            record = cur.fetchone()[0] 
            return {
                "deleted_features":record
                    }
        elif mode == "update_deleted_features" :
            #sample body: {"mode":"update_deleted_features","deleted_feature_ids":[8,3,4],"table_name":"pois" ,"scenario_id":"2"} */

            cur.execute(
            f"""UPDATE scenarios SET {translation_layers[body.get('table_name')]} = array{body.get('deleted_feature_ids')}::bigint[] WHERE scenario_id = {body.get('scenario_id')}::bigint""")
            con.commit()
            return{
                "updated_succes":True
            }
        elif mode == "delete_feature" :
            #delete is used to delete the feature from modified table if the user has drawn that feature by himself
            #sample body: {"mode":"delete_feature","table_name":"pois","scenario_id":"8","deleted_feature_ids":[2,3,4],"drawned_fid":"14"} */
            print( f"""DELETE FROM {body.get('table_name')}_modified WHERE scenario_id = {body.get('scenario_id')}::bigint AND original_id = ANY((array{body.get('deleted_feature_ids')}))
            """)
            cur.execute(
            f"""DELETE FROM {body.get('table_name')}_modified WHERE scenario_id = {body.get('scenario_id')}::bigint AND original_id = ANY((array{body.get('deleted_feature_ids')}))
            """)
            cur.execute(
            f"""DELETE FROM {body.get('table_name')}_modified WHERE gid=({body.get('drawned_fid')});"""
            )
            con.commit()
            return{
                'deleted_success':True
                    }
        elif mode == "insert" :
        #/*sample body: {mode:"insert","userid":1,"scenario_name":"scenario1"}*/
            cur.execute(f"""
            INSERT INTO scenarios (userid, scenario_name) VALUES ({body.get('userid')},'{body.get('scenario_name')}') RETURNING scenario_id
            """)
            record = cur.fetchone()[0] 
            con.commit()
            return {
                "scenario_id":record
                    }
        elif mode == "delete": 
        #/*sample body: {mode:"delete","scenario_id":97}*/
            cur.execute(
            f"""DELETE FROM scenarios WHERE scenario_id = {body.get('scenario_id')}::bigint"""
            )
            con.commit()
            return{
                "deleted_success":True
            }
        elif mode == "update_scenario" :
        #/*sample body: {mode:"update_scenario","scenario_id":2,"scenario_name":"new_name2"}*/
            cur.execute(
        f"""UPDATE scenarios SET scenario_name = '{body.get('scenario_name')}' WHERE scenario_id = {body.get('scenario_id')}::bigint
        """
        )
            con.commit()
            return{
                "update_success":True
            }
    except(Exception, psycopg2.Error) as error:
        print("Postgres Error", error)
        con = None

    finally:
        if(con != None):
            cur.close()
            con.close()
            print("PostgreSQL connection is now closed")


@app.route("/api/isochrone", methods=["POST"])
def isochrone():
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
    "routing_profile",
    ]
    queryValues = []

    for key in  requiredParams :
        value = body[key]
        if key not in body.keys(): 
            return 'key error'  
        queryValues.append(value)

    #// Make sure to set the correct content type
    #response.set("content-type", "application/json");
    try:
        con = psycopg2.connect("host={} dbname={} user={} password={} port = {}".format(host,db_name,db_user,db_password,port))
        cur=con.cursor()
        cur.execute(
        f"""SELECT jsonb_build_object(
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
        FROM (SELECT * FROM isochrones_api ({queryValues[0]},{queryValues[1]},{queryValues[2]},{queryValues[3]},{queryValues[4]},{queryValues[5]},{queryValues[6]},'{queryValues[7]}','{queryValues[8]}','{queryValues[9]}',NULL,NULL,NULL)) inputs) features;""")
        json_record=cur.fetchone()[0]
        return json_record
    except(Exception, psycopg2.Error) as error:
        print("Postgres Error", error)
        con = None
    finally:
        if(con != None):
            cur.close()
            con.close()
            print("PostgreSQL connection is now closed")


@app.route("/api/userdata", methods=["POST"])
def manage_user():
    body=request.get_json()
    mode=body.get('mode')
    try:
        con = psycopg2.connect("host={} dbname={} user={} password={} port = {}".format(host,db_name,db_user,db_password,port))
        cur=con.cursor()
        if mode == "insert":
            print('hello')
            cur.execute("INSERT INTO user_data (username, pw) VALUES ('','') RETURNING userid")
            record = cur.fetchone()[0]
            con.commit()
            return {
                    'userid': f"{record}"
                    }
        elif mode == "delete":
            #/*sample body: {"mode":"delete", "userid":1}*/
                cur.execute(f"""DELETE FROM user_data WHERE userid = {body.get('userid')}::bigint""")
                con.commit()
                return{
                    'deleted_success':True
                }
    except(Exception, psycopg2.Error) as error:
        print("Postgres Error", error)
        con = None

    finally:
        if(con != None):
            cur.close()
            con.close()
            print("PostgreSQL connection is now closed")    

@app.route("/api/count_pois_multi_isochrones", methods=["POST"])
def count_pois_multi_isochrones():
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
    try:
        con = psycopg2.connect("host={} dbname={} user={} password={} port = {}".format(host,db_name,db_user,db_password,port))
        cur=con.cursor()
        sqlQuery = f"""SELECT jsonb_build_object(
        'type',       'Feature',
        'geometry',   ST_AsGeoJSON(geom)::jsonb,
        'properties', to_jsonb(inputs) - 'geom'
    ) AS feature 
    FROM (SELECT count_pois,region_name, geom FROM count_pois_multi_isochrones({queryValues[0]},{queryValues[1]},{queryValues[2]},{queryValues[3]},{queryValues[4]},{queryValues[5]},'{queryValues[6]}',array[{queryValues[7]}])) inputs;"""
        cur.execute(sqlQuery)
        record=cur.fetchone()[0]
        return record
    except(Exception, psycopg2.Error) as error:
        print("Postgres Error", error)
        con = None

    finally:
        if(con != None):
            cur.close()
            con.close()
            print("PostgreSQL connection is now closed")  


def async_action(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

async def fun_task1(cur,scenarioId):
    #//1- Delete from scenario first
    await asyncio.sleep(1)
    cur.execute(f"""SELECT * FROM network_modification({scenarioId});""")
    

async def fun_task2(cur,scenarioId):
    #//2- Rerun upload for ways to reflect the changes.
    await asyncio.sleep(2)
    cur.execute(f"""SELECT * FROM population_modification({scenarioId});""")
    

@app.route("/api/upload_all_scenarios", methods=["POST"])
@async_action
async def upload_all_scenarios():
    body=request.get_json()
    scenarioId = body.get('scenario_id')
    try:
        con = psycopg2.connect("host={} dbname={} user={} password={} port = {}".format(host,db_name,db_user,db_password,port))
        cur=con.cursor()
        task1 = asyncio.create_task(fun_task1(cur,scenarioId))
        task2 = asyncio.create_task(fun_task2(cur,scenarioId))

        # Wait until both tasks are completed (should take
        # around 2 seconds.)
        await task1
        await task2
        network_modification_record=cur.fetchall()
        population_modification_record=cur.fetchall()
        return {'network_modification':network_modification_record,
                'population_modification':population_modification_record
        }
    except(Exception, psycopg2.Error) as error:
        print("Postgres Error", error)
        con = None
    finally:
        if(con != None):
            cur.close()
            con.close()
            print("PostgreSQL connection is now closed")  


@app.route("/api/import_scenario",methods=["POST"])
def import_scenario():
    body=request.get_json()
    try:
        con = psycopg2.connect("host={} dbname={} user={} password={} port = {}".format(host,db_name,db_user,db_password,port))
        cur=con.cursor()
        payload =  json.dumps(body.get('payload'), separators=(',', ':'))
        cur.execute(f"SELECT import_changeset_scenario({body.get('scenario_id')}, {body.get('user_id')},jsonb_build_object('{body.get('layerName')}','{payload}'::jsonb))")
        record = cur.fetchone()[0]
        return record
    except(Exception, psycopg2.Error) as error:
        print("Postgres Error", error)
        con = None
    finally:
        if(con != None):
            cur.close()
            con.close()
            print("PostgreSQL connection is now closed") 
 
@app.route("/api/pois_multi_isochrones", methods=["POST"])
def pois_multi_isochrones():
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
    try:
        con = psycopg2.connect("host={} dbname={} user={} password={} port = {}".format(host,db_name,db_user,db_password,port))
        cur=con.cursor()
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
        cur.execute(sqlQuery)
        record = cur.fetchone()[0]
        return record
    except(Exception, psycopg2.Error) as error:
        print("Postgres Error", error)
        con = None
    finally:
        if(con != None):
            cur.close()
            con.close()
            print("PostgreSQL connection is now closed")  


@app.route("/api/export_scenario",methods=["POST"])
def export():
    body=request.get_json() 
    try:
        con = psycopg2.connect("host={} dbname={} user={} password={} port = {}".format(host,db_name,db_user,db_password,port))
        cur=con.cursor()
        cur.execute(f"""SELECT * FROM export_changeset_scenario({body.get('scenario_id')})""")
        record = cur.fetchone()[0]
        dicts = record
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
    except(Exception, psycopg2.Error) as error:
        print("Postgres Error", error)
        con = None
    finally:
        if(con != None):
            cur.close()
            con.close()
            print("PostgreSQL connection is now closed")  


if __name__ == '__main__':
    app.run(host ='0.0.0.0',port=3001)