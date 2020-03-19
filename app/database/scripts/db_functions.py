#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml, os, psycopg2, glob
class ReadYAML:
    with open("/opt/config/goat_config.yaml", 'r') as stream:
        conf = yaml.load(stream, Loader=yaml.FullLoader)
   
    db_conf = conf["DATABASE"]
    source_conf = conf["DATA_SOURCE"]
    refinement_conf = conf["DATA_REFINEMENT_VARIABLES"]

    def db_credentials(self):
        return self.db_conf["DB_NAME"],self.db_conf["USER"],self.db_conf["HOST"],self.db_conf["PORT"],self.db_conf["PASSWORD"]
    def data_source(self):
        return self.source_conf["OSM_DOWNLOAD_LINK"],self.source_conf["OSM_DATA_RECENCY"],self.source_conf["BUFFER_BOUNDING_BOX"],self.source_conf["EXTRACT_BBOX"],self.refinement_conf["POPULATION"],self.refinement_conf["ADDITIONAL_WALKABILITY_LAYERS"]
    def data_refinement(self):
        return self.refinement_conf
    def create_pgpass(self,db_prefix):
        db_name = self.db_conf["DB_NAME"]+db_prefix
        os.system('echo '+':'.join([self.db_conf["HOST"],str(self.db_conf["PORT"]),db_name,self.db_conf["USER"],self.db_conf["PASSWORD"]])+' > /.pgpass')
        os.system("chmod 600 /.pgpass")
    
class DB_connection:
    def __init__(self, db_name, user, host):
        self.db_name = db_name
        self.user = user
        self.host = host

    def execute_script_psql(self,script):
        os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (self.db_name,self.user,self.host,script))
    def execute_text_psql(self,script):
        os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -c "%s"' % (self.db_name,self.user,self.host,script))
    def con_psycopg(self,port,password):
        con = psycopg2.connect("dbname='%s' user='%s' host='%s' port = '%s' password='%s'" % (
        self.db_name,self.user,port,self.host,password))
        return con.cursor()

def create_variable_container():
    sql_create_table = '''DROP TABLE IF EXISTS variable_container;
    CREATE TABLE public.variable_container (
	identifier varchar(100) NOT NULL,
	variable_simple text NULL,
	variable_array text[] NULL,
	variable_object jsonb NULL,
	CONSTRAINT variable_container_pkey PRIMARY KEY (identifier)
    );'''
    variable_object = ReadYAML().data_refinement()['variable_container']
    sql_simple = "INSERT INTO variable_container(identifier,variable_simple) VALUES('%s',%s);"
    sql_array = "INSERT INTO variable_container(identifier,variable_array) VALUES('%s',ARRAY%s);"
    sql_object = "INSERT INTO  variable_container(identifier,variable_object) SELECT '%s', jsonb_build_object(%s);"
    sql_insert=''
    for i in variable_object.keys():
        v = variable_object[i] 
        if isinstance(v,str):
            sql_insert = sql_insert + (sql_simple % (i,v))
        elif isinstance(v,list):
            sql_insert = sql_insert + (sql_array % (i,v))
        elif isinstance(v,object):
            objs = ''
            for k in v.keys():
                if isinstance(v[k],list):
                    objs = objs+ ",'%s', ARRAY%s" % (k,v[k])
                elif isinstance(v[k],object):
                    objs = objs + ",'%s','%s'" % (k,v[k])
            sql_insert = sql_insert + sql_object % (i,objs[1:])
                
    return sql_create_table + sql_insert


def update_functions():
    from pathlib import Path
    import glob
    db_name,user,host = ReadYAML().db_credentials()[:3]
    db = DB_connection(db_name,user,host)
    db.execute_script_psql('/opt/data_preparation/SQL/types.sql')
    for p in ['/opt/database_functions/other','/opt/database_functions/network','/opt/database_functions/routing','/opt/database_functions/heatmap']:
        for file in Path(p).glob('*.sql'):
            db.execute_script_psql(file)

def geojson_to_sql():
    import json, glob
    from geojson import FeatureCollection, Point
    
    def check_valid(attr,keys):
        if attr in keys:
                o = feature['properties'][attr]
                if o is not None and o != 'null' and o != 'NULL':
                    x = o.replace("'","''")
                    return x
    con = psycopg2.connect("dbname='%s' user='%s' port = '%s' host='%s' password='%s'" % (
    'goat','goat','5432','localhost','earlmanigault'))
    cursor = con.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS custom_pois;')
    cursor.execute('CREATE TABLE custom_pois(amenity text, addr_street text,addr_city text, addr_postcode text, name text, opening_hours text, geom geometry, stand_name text);')   

    for file in glob.glob("/opt/data/custom_pois/*.geojson"):
        with open(file, 'r') as stream:
            data = json.load(stream)
        print(file)
   
        sql_insert_empty = '''INSERT INTO custom_pois(amenity,addr_street,addr_city,addr_postcode,name,opening_hours,geom, stand_name) VALUES('%s','%s','%s','%s','%s','%s',%s,'%s');''' 
        sql_bulk = '' 
        for feature in data['features']:
            amenity = file.split('/')[-1].split('-')[0]          
            sql_insert_columns = ''
            keys = feature['properties'].keys()
            addr_street = check_valid('addr:street',keys)
            addr_postcode = check_valid('addr_postcode',keys)
            addr_city = check_valid('addr:city',keys)
            name = check_valid('name',keys)
            stand_name = file.split('/')[-1].split('-')[1].split('.')[0]
            if name is None:
                name = file.split('/')[-1].split('-')[1].split('.')[0]
            opening_hours = check_valid('opening_hours',keys)

            if feature['geometry'] is not None:
                geom = "ST_SetSRID(ST_GeomFromGeoJSON('%s'),4326)" % str(feature['geometry']).replace("'",'"') 
                sql_insert_filled = sql_insert_empty % (amenity,addr_street,addr_city,addr_postcode,name,opening_hours, geom, stand_name)
                sql_bulk = sql_bulk + sql_insert_filled         
        cursor.execute(sql_bulk)       
        con.commit()
    con.close()
    return sql_bulk

#x = geojson_to_sql()

def find_newest_dump(namespace):
    import os
    fnames = []
    for file in os.listdir("/opt/backups"):
        if file.endswith(".sql") and namespace == file.split('_')[0]:
            fnames.append(file)
    newest_file = sorted(fnames)[-1]

    return newest_file

def restore_db(namespace):
    import os
    
    newest_file = find_newest_dump(namespace)

    db_name,user = ReadYAML().db_credentials()[:2]
    #Drop backup db tags as old DB
    os.system('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % (db_name+'old'))
    os.system('psql -U postgres -c "DROP DATABASE %s;"' % (db_name+'old'))
    os.system('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % (db_name+'temp'))
    os.system('psql -U postgres -c "DROP DATABASE IF EXISTS %s;"' % (db_name+'temp'))
    #Restore backup as temp db
    os.system("psql -U postgres -c 'CREATE DATABASE %s;'"% (db_name+'temp'))
    os.system('psql -U %s -d %s -f /opt/backups/%s' % (user,db_name+'temp',newest_file))
    #Rename active database into old DB
    os.system('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % db_name)
    os.system('psql -U postgres -c "ALTER DATABASE %s RENAME TO %s;"' % (db_name,db_name+'old'))
    #Rename temp DB into active db
    os.system('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % (db_name+'temp'))
    os.system('psql -U postgres -c "ALTER DATABASE %s RENAME TO %s;"' % (db_name+'temp',db_name))

