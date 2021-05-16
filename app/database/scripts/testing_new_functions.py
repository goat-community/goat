
import os 
os.environ['POSTGRES_DBNAME_TEMP'] = 'goattemp'
from db.db import Database
from db_functions import ReadYAML
from psycopg2 import sql
from urllib.request import urlretrieve
import subprocess
import yaml
import json 

db_conn = Database()

class CreateDatabase():
    def __init__(self, db_conf):
        self.db_name = db_conf["DB_NAME"]
        self.user = db_conf["USER"]
        self.host = db_conf["HOST"]
        self.db_name_temp = self.db_name+'temp'

    def create_fresh_temp_db(self):
        subprocess.run(f'''PGPASSFILE=~/.pgpass_{self.db_name} psql -U {self.user} -h {self.host} -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{self.db_name_temp}';"''', shell=True, check=True)
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name} psql -U {self.user} -h {self.host} -c "DROP DATABASE IF EXISTS {self.db_name_temp};"', shell=True, check=True)
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name} psql -U {self.user} -h {self.host} -c "CREATE DATABASE {self.db_name_temp};"', shell=True, check=True)
    
        #Create extensions
        subprocess.run(F'PGPASSFILE=~/.pgpass_{self.db_name_temp} psql -U {self.user} -h {self.host} -d {self.db_name_temp} -c "CREATE EXTENSION postgis;CREATE EXTENSION pgrouting;CREATE EXTENSION hstore;CREATE EXTENSION intarray;CREATE EXTENSION plpython3u;"', shell=True, check=True)
        subprocess.run(F'PGPASSFILE=~/.pgpass_{self.db_name_temp} psql -U {self.user} -h {self.host} -d {self.db_name_temp} -c "CREATE EXTENSION arraymath;CREATE EXTENSION floatvec;"', shell=True, check=True)

        #These extensions are needed when using the new DB-image
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name_temp} psql -U {self.user} -h {self.host} -d {self.db_name_temp} -c "CREATE EXTENSION postgis_raster;"', shell=True, check=True)
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name_temp} psql -U {self.user} -h {self.host} -d {self.db_name_temp} -c "CREATE EXTENSION plv8;"', shell=True, check=True)

class OsmImport():
    def __init__(self, db_conf, goat_conf, is_temp):
        self.db_name = db_conf["DB_NAME"]
        self.user = db_conf["USER"]
        self.host = db_conf["HOST"]
        if is_temp == True: 
            self.db_name = self.db_name + 'temp'

        self.download_link = goat_conf["DATA_SOURCE"]["OSM_DOWNLOAD_LINK"]
        self.buffer = float(goat_conf["DATA_SOURCE"]["BUFFER_BOUNDING_BOX"])
        self.extract_bbox = goat_conf["DATA_SOURCE"]["EXTRACT_BBOX"]

    def prepare_planet_osm(self):
        os.chdir('/opt/data') 
        if self.download_link != 'no_download':     
            print('Fresh OSM-data will be download from: %s' % self.download_link)
            result = subprocess.run(f'wget --no-check-certificate --output-document="raw-osm.osm.pbf" {self.download_link}', shell=True, check=True)

            if result.returncode != 0:
                return {"Error": "Download not successful"}

        if self.extract_bbox == "yes":
            db_conn.perform(open('/opt/database_functions/data_preparation/create_bbox_study_area.sql', "r").read())
            bboxes = db_conn.select('SELECT * FROM create_bbox_study_area(%(buffer)s)', params={"buffer":self.buffer})[0][0]
            subprocess.run(f'osmosis --read-pbf file="raw-osm.osm.pbf" {bboxes} --write-xml file="study_area.osm"', shell=True, check=True)
        elif self.extract_bbox == "no_extract":
            subprocess.run(f'osmosis --read-pbf file="raw-osm.osm.pbf" --write-xml file="study_area.osm"', shell=True, check=True)

        subprocess.run('osmconvert study_area.osm --drop-author --drop-version --out-osm -o=study_area_reduced.osm', shell=True, check=True)
        subprocess.run('rm study_area.osm | mv study_area_reduced.osm study_area.osm', shell=True, check=True)
    
    def import_osm2pgsql(self):
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name} osm2pgsql -d {self.db_name} -H {self.host} -U {self.user} --hstore -E 4326 -c /opt/data/study_area.osm', shell=True, check=True) 

    def import_raw_layer(self, filepath):
        filename = os.path.basename(filepath) 
        data_type = filename.split('.')[1]
        table_name = filename.split('.')[0]

        print("The following file will be imported: %s" % filename)

        db_conn.perform(sql.SQL('DROP TABLE IF EXISTS {}').format(sql.Identifier(table_name)))
        if data_type == 'shp':
            subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name} shp2pgsql -I -s 4326  %s public.%s | PGPASSFILE=~/.pgpass_{self.db_name} psql -d %s -U %s -h %s -q' 
            % (filepath,table_name,self.db_name,self.user,self.host), shell=True, check=True) 
        elif data_type == 'sql':
            #db_conn.perform(open(filepath, "r").read())
            subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name} psql -d %s -U %s -h %s -f %s -q' % (self.db_name,self.user,self.host,filepath), shell=True, check=True) 
        else:
            return 

class FileHelper():
    @staticmethod
    def list_files_dir(filepath, ending):
        file_list = []
        for root, dirs, files in os.walk(filepath):
            for filename in files:
                if filename.endswith(ending):
                    file_list.append(filename)
        return file_list

    @staticmethod
    def list_files_for_import(filenames, ending_priority, table_names):
        filenames = list(filter(lambda f: f.split('.')[0] in table_names, filenames))
        
        cleaned_list = []
        for filename in filenames: 
            if filename.endswith(ending_priority): 
                cleaned_list.append(filename)
            elif not filename.endswith(ending_priority) and filename.split('.')[0] + ending_priority not in filenames:
                cleaned_list.append(filename)

        return cleaned_list
   
class PrepareDatabase():
    def __init__(self, db_conf, goat_conf, is_temp):
        self.db_name = db_conf["DB_NAME"]
        self.user = db_conf["USER"]
        self.host = db_conf["HOST"]
        if is_temp == True: 
            self.db_name = self.db_name + 'temp'

        self.mapping_conf = ReadYAML().return_mapping_conf()
        self.data_refinement = ReadYAML().return_data_refinement()

    def create_variable_container(self):
        db_conn.perform('''DROP TABLE IF EXISTS variable_container;
        CREATE TABLE public.variable_container (
        identifier varchar(100) NOT NULL,
        variable_simple text NULL,
        variable_array text[] NULL,
        variable_object jsonb NULL,
        CONSTRAINT variable_container_pkey PRIMARY KEY (identifier)
        )''')
        
        variable_object = {**self.data_refinement['variable_container'],**self.mapping_conf}

        sql_simple = "INSERT INTO variable_container(identifier,variable_simple) VALUES('%s',%s);"
        sql_array = "INSERT INTO variable_container(identifier,variable_array) VALUES('%s',ARRAY%s);"
        sql_object = "INSERT INTO  variable_container(identifier,variable_object) SELECT '%s', jsonb_build_object(%s);"
        sql_insert=''

        for i in variable_object.keys():
            v = variable_object[i] 
            if isinstance(v,str):
                sql_insert = sql_simple % (i,v)
            elif isinstance(v,list):
                sql_insert = sql_array % (i,v)
            elif isinstance(v,object):
                sql_insert = "INSERT INTO variable_container (identifier,variable_object) VALUES ( '{0}','{1}' );\n".format(i,json.dumps(v).strip())
            db_conn.perform(sql_insert)

    def execute_script_psql(self,script):
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name} psql -d {self.db_name} -U {self.user} -h {self.host} -f {script}', shell=True, check=True) 

    def execute_bulk_sql(self, directory):
        for root, dirs, files in os.walk(directory):
            for name in files:
                if name.endswith(".sql"): 
                    self.execute_script_psql(os.path.join(root, name))

    def update_functions(self):
        db_conn.perform(open('/opt/data_preparation/SQL/types.sql', "r").read())
        for p in ['/opt/database_functions/other','/opt/database_functions/network','/opt/database_functions/routing','/opt/database_functions/heatmap','/opt/database_functions/data_preparation', '/opt/database_functions/layers_api']:
            self.execute_bulk_sql(p)

    def data_preparation_table_types_functions(self):
        db_conn.perform(open('/opt/data_preparation/SQL/create_tables.sql', "r").read())
        self.create_variable_container()
        db_conn.perform(open('/opt/data_preparation/SQL/types.sql', "r").read())

        self.execute_bulk_sql('/opt/database_functions/data_preparation')

    
        


ReadYAML().create_pgpass('','goat')
ReadYAML().create_pgpass('temp','goat')

db_conf = ReadYAML().return_db_conf()
goat_conf = ReadYAML().return_goat_conf()

#CreateDatabase(db_conf).create_fresh_temp_db()

#cls_import = OsmImport(db_conf,goat_conf,True)
#cls_import.prepare_planet_osm()
#cls_import.import_osm2pgsql()


#PrepareDatabase(db_conf,goat_conf,True).create_variable_container()
#PrepareDatabase(db_conf,goat_conf,True).update_functions()
#PrepareDatabase(db_conf,goat_conf,True).data_preparation_table_types_functions()

prepare_db = PrepareDatabase(db_conf,goat_conf,True)

#PrepareDatabase(db_conf,goat_conf,True).execute_script_psql('/opt/data_preparation/SQL/create_tables.sql')

class Population():
    @staticmethod
    def prepare_data():
        raw_files = FileHelper().list_files_for_import(
            FileHelper().list_files_dir('/opt/data/', ('.shp','.sql')), '.sql',
            ['buildings_custom','population','study_area','landuse','landuse_additional','pois']
        )

        for f in raw_files:
            cls_import.import_raw_layer('/opt/data/'+f)

    def produce_population_points(self, source_population):

        print ('It was chosen to use population from: ', source_population)
        prepare_db.execute_script_psql('/opt/data_preparation/SQL/landuse_osm.sql')
        prepare_db.execute_script_psql('/opt/data_preparation/SQL/data_fusion_buildings.sql')
        prepare_db.execute_script_psql('/opt/data_preparation/SQL/classify_buildings.sql')

        #if db.select("SELECT * FROM to_regclass('public.buildings_custom')")[0][0] != None:
            #Data fusion of OSM building and custom buildings
        #    script_buildings = 'buildings_residential_custom.sql'
        #else:
        #    script_buildings = 'buildings_residential.sql'

        #if (source_population == 'extrapolation'):
        #    db_conn.perform(open('/opt/data_preparation/SQL/'+script_buildings, "r").read())

            #db_temp.execute_script_psql('../data_preparation/SQL/'+script_buildings)
            #db_temp.execute_script_psql('../data_preparation/SQL/census.sql')
        #elif(source_population == 'disaggregation'):
        #    db_conn.execute_script_psql('/opt/data_preparation/SQL/'+script_buildings)
        #    db_conn.execute_script_psql('/opt/data_preparation/SQL/population_disagregation.sql')
        #elif(source_population == 'distribution'):
        #    db_conn.execute_script_psql('/opt/data_preparation/SQL/population_distribution.sql')

        #db_conn.perform('../data_preparation/SQL/create_population_userinput.sql')

Population().produce_population_points('extrapolation')

os.environ['POSTGRES_DBNAME'] = 'goat'
