#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml, os, psycopg2
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

def load_js_lib():
    import os 
    db_name,user = ReadYAML().db_credentials()[:2]
    os.system(f'psql -U {user} -d {db_name} -c "DROP TABLE IF EXISTS plv8_js_modules;"')
    os.system(f'psql -U {user} -d {db_name} -f /opt/database_functions/libs/plv8_js_modules.sql')
    os.system(f'psql -U {user} -d {db_name} -c "ALTER DATABASE {db_name} SET plv8.start_proc TO plv8_require"')

#load_js_lib()