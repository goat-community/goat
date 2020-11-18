#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml, os, psycopg2, glob
class ReadYAML:
    with open("/opt/config/db/db.yaml", 'r') as stream:
        db_conf = yaml.load(stream, Loader=yaml.FullLoader)
  
    with open("/opt/config/goat_config.yaml", 'r') as stream:
        goat_conf = yaml.load(stream, Loader=yaml.FullLoader)
    
    with open("/opt/config/osm_mapping_config.yaml", 'r') as stream:
        osm_mapping_conf = yaml.load(stream, Loader=yaml.FullLoader)

    source_conf = goat_conf["DATA_SOURCE"]
    refinement_conf = goat_conf["DATA_REFINEMENT_VARIABLES"]

    def db_credentials(self):
        return self.db_conf["DB_NAME"],self.db_conf["USER"],self.db_conf["HOST"],self.db_conf["PORT"],self.db_conf["PASSWORD"]
    def data_source(self):
        return self.source_conf["OSM_DOWNLOAD_LINK"],self.source_conf["OSM_DATA_RECENCY"],self.source_conf["BUFFER_BOUNDING_BOX"],self.source_conf["EXTRACT_BBOX"],self.refinement_conf["POPULATION"],self.refinement_conf["ADDITIONAL_WALKABILITY_LAYERS"],self.refinement_conf["OSM_MAPPING_FEATURE"]
    def data_refinement(self):
        return self.refinement_conf
    def create_pgpass(self,db_prefix,user):
        db_name = self.db_conf["DB_NAME"] + db_prefix
        os.system('echo '+':'.join([self.db_conf["HOST"],str(self.db_conf["PORT"]),db_name,user,self.db_conf["PASSWORD"]])+f' > ~/.pgpass_{db_name}')
        os.system(f'chmod 600  ~/.pgpass_{db_name}')
    def mapping_conf(self):
        return self.osm_mapping_conf

class DB_connection:
    def __init__(self, db_name, user, host,port,password):
        self.db_name = db_name
        self.user = user
        self.host = host
        self.port = port 
        self.password = password

    def execute_script_psql(self,script):
        os.system(f'PGPASSFILE=~/.pgpass_{self.db_name} psql -d {self.db_name} -U {self.user} -h {self.host} -f {script}')
    def execute_text_psql(self,script):
        os.system(f'PGPASSFILE=~/.pgpass_{self.db_name} psql -d {self.db_name} -U {self.user} -h {self.host} -c "{script}"')
    def con_psycopg(self):
        con = psycopg2.connect("dbname='%s' user='%s' host='%s' port = '%s' password='%s'" % (
        self.db_name,self.user,self.host,self.port,self.password))
        return con, con.cursor()


def bulk_compute_slope(db_name,user,port,host,password):
    import psycopg2

    con = psycopg2.connect("dbname='%s' user='%s' port = '%s' host='%s' password='%s'" % (db_name,user,str(port),host,password))
    cursor = con.cursor()

    cursor.execute('SELECT count(*) FROM ways;')
    cnt_ways = cursor.fetchall()[0][0]

    sql_way_ids = '''SELECT id
    FROM ways 
    WHERE class_id::text NOT IN(SELECT UNNEST(select_from_variable_container('excluded_class_id_cycling')));'''
    cursor.execute(sql_way_ids)
    way_ids = cursor.fetchall()

    cnt = 0
    for i in way_ids:
    
        cnt = cnt + 1 
        if (cnt/1000).is_integer():
            print('Impedance for %s out of %s ways' % (cnt,cnt_ways)) 
            con.commit()

        sql_compute_slope = 'SELECT update_impedance(%s::integer)' % (i[0])
        cursor.execute(sql_compute_slope)
#bulk_compute_slope('goat','goat','5432','localhost','earlmanigault')

def create_variable_container(db_name,user,port,host,password):
    import json 
    import psycopg2

    con = psycopg2.connect("dbname='%s' user='%s' port = '%s' host='%s' password='%s'" % (db_name,user,str(port),host,password))
    cursor = con.cursor()

    sql_create_table = '''DROP TABLE IF EXISTS variable_container;
    CREATE TABLE public.variable_container (
	identifier varchar(100) NOT NULL,
	variable_simple text NULL,
	variable_array text[] NULL,
	variable_object jsonb NULL,
	CONSTRAINT variable_container_pkey PRIMARY KEY (identifier)
    );'''
    
    variable_object = {**ReadYAML().data_refinement()['variable_container'],**ReadYAML().mapping_conf()}

    sql_simple = "INSERT INTO variable_container(identifier,variable_simple) VALUES('%s',%s);"
    sql_array = "INSERT INTO variable_container(identifier,variable_array) VALUES('%s',ARRAY%s);"
    sql_object = "INSERT INTO  variable_container(identifier,variable_object) SELECT '%s', jsonb_build_object(%s);"
    sql_insert=''

    cursor.execute(sql_create_table)
    con.commit()
    for i in variable_object.keys():
        v = variable_object[i] 
        if isinstance(v,str):
            sql_insert = sql_simple % (i,v)
        elif isinstance(v,list):
            sql_insert = sql_array % (i,v)
        elif isinstance(v,object):
            sql_insert = "INSERT INTO variable_container (identifier,variable_object) VALUES ( '{0}','{1}' );\n".format(i,json.dumps(v).strip())
        cursor.execute(sql_insert)
    con.commit()

def update_functions():
    from pathlib import Path
    import glob
    db_name,user,host,port,password = ReadYAML().db_credentials()
    db = DB_connection(db_name,user,host,port,password)
    db.execute_script_psql('/opt/data_preparation/SQL/types.sql')
    for p in ['/opt/database_functions/other','/opt/database_functions/network','/opt/database_functions/routing','/opt/database_functions/heatmap','/opt/database_functions/data_preparation']:
        for file in Path(p).glob('*.sql'):
            db.execute_script_psql(file)

def geojson_to_sql(db_name,user,host,port,password):
    import json, glob

    def check_valid(attr,keys):
        if attr in keys:
                o = feature['properties'][attr]
                if o is not None and o != 'null' and o != 'NULL':
                    x = o.replace("'","''")
                    return x
    con = psycopg2.connect("dbname='%s' user='%s' port = '%s' host='%s' password='%s'" % (db_name,user,str(port),host,password))
    cursor = con.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS custom_pois;')
    cursor.execute('''CREATE TABLE custom_pois
                    (gid serial,amenity text, addr_street text,addr_city text, addr_postcode text, 
                    name text, opening_hours text, geom geometry(POINT, 4326), stand_name text, 
                    CONSTRAINT custom_pois_gid_pkey PRIMARY KEY (gid));''')
    cursor.execute('CREATE INDEX ON custom_pois USING GIST(geom);')
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

#geojson_to_sql('goat','goat','localhost',5432,'earlmanigault')

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