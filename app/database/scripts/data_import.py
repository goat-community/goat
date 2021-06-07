import subprocess
import os 
from psycopg2 import sql

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

class DataImport():
    def __init__(self, read_yaml_config, is_temp, db_conn):
        self.db_conf = read_yaml_config.return_db_conf()
        self.db_name = self.db_conf["DB_NAME"]
        self.user = self.db_conf["USER"]
        self.host = self.db_conf["HOST"]
        if is_temp == True: 
            self.db_name = self.db_name + 'temp'

        self.download_link = read_yaml_config.goat_conf["DATA_SOURCE"]["OSM_DOWNLOAD_LINK"]
        self.buffer = float(read_yaml_config.goat_conf["DATA_SOURCE"]["BUFFER_BOUNDING_BOX"])
        self.extract_bbox = read_yaml_config.goat_conf["DATA_SOURCE"]["EXTRACT_BBOX"]
        self.db_conn = db_conn

    def prepare_planet_osm(self):
        os.chdir('/opt/data') 
        if self.download_link != 'no_download':     
            print('Fresh OSM-data will be download from: %s' % self.download_link)
            result = subprocess.run(f'wget --no-check-certificate --output-document="raw-osm.osm.pbf" {self.download_link}', shell=True, check=True)

            if result.returncode != 0:
                return {"Error": "Download not successful"}

        if self.extract_bbox == "yes":
            self.db_conn.perform(open('/opt/database_functions/data_preparation/create_bbox_study_area.sql', "r").read())
            bboxes = self.db_conn.select('SELECT * FROM create_bbox_study_area(%(buffer)s)', params={"buffer":self.buffer})[0][0]
            subprocess.run(f'osmosis --read-pbf file="raw-osm.osm.pbf" {bboxes} --write-xml file="study_area.osm"', shell=True, check=True)
        elif self.extract_bbox == "no_extract":
            subprocess.run(f'osmosis --read-pbf file="raw-osm.osm.pbf" --write-xml file="study_area.osm"', shell=True, check=True)

        subprocess.run('osmconvert study_area.osm --drop-author --drop-version --out-osm -o=study_area_reduced.osm', shell=True, check=True)
        subprocess.run('rm study_area.osm | mv study_area_reduced.osm study_area.osm', shell=True, check=True)
    
    def import_osm2pgsql(self):
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name} osm2pgsql -d {self.db_name} -H {self.host} -U {self.user} --hstore -E 4326 -c /opt/data/study_area.osm', shell=True, check=True) 

    def import_osm2pgrouting(self):
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name} osm2pgrouting --dbname {self.db_name} --host {self.host} --username {self.user} --file "/opt/data/study_area.osm" --conf /opt/config/mapconfig.xml --clean', shell=True, check=True) 
     
    def import_raw_layer(self, filepath):
        filename = os.path.basename(filepath) 
        data_type = filename.split('.')[1]
        table_name = filename.split('.')[0]

        print("The following file will be imported: %s" % filename)

        self.db_conn.perform(sql.SQL('DROP TABLE IF EXISTS {}').format(sql.Identifier(table_name)))
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