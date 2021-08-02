import subprocess
import os 
from psycopg2 import sql
import yaml 
import json
import fiona
import geopandas as gpd
import logging
import json

class ReadYAML():
    """Read and return database configuration."""
    def __init__(self):
        with open("/opt/config/db/db.yaml", 'r') as stream:
            self.db_conf = yaml.load(stream, Loader=yaml.FullLoader)
    
        with open("/opt/config/goat_config.yaml", 'r') as stream:
            self.goat_conf = yaml.load(stream, Loader=yaml.FullLoader)
        
        with open("/opt/config/osm_mapping_config.yaml", 'r') as stream:
            self.osm_mapping_conf = yaml.load(stream, Loader=yaml.FullLoader)

    def return_db_conf(self):
        return self.db_conf
    def return_goat_conf(self):
        return self.goat_conf
    def return_mapping_conf(self):
        return self.osm_mapping_conf
    def create_pgpass(self,db_prefix,user):
        db_name = self.db_conf["DB_NAME"] + db_prefix
        os.system('echo '+':'.join([self.db_conf["HOST"],str(self.db_conf["PORT"]),db_name,user,self.db_conf["PASSWORD"]])+f' > ~/.pgpass_{db_name}')
        os.system(f'chmod 600  ~/.pgpass_{db_name}')

class CreateDatabase():
    """For creating a database with the required configurations and extensions"""
    def __init__(self, read_yaml_config):
        self.read_yaml_config = read_yaml_config
        self.db_conf = read_yaml_config.return_db_conf()
        self.db_name = self.db_conf["DB_NAME"]
        self.user = self.db_conf["USER"]
        self.host = self.db_conf["HOST"]
        self.password = self.db_conf["PASSWORD"]
        self.db_name_temp = self.db_name+'temp'

    def create_fresh_temp_db(self):
        #Create fresh temporary database
        subprocess.run(f'''PGPASSFILE=~/.pgpass_{self.db_name} psql -U {self.user} -h {self.host} -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{self.db_name_temp}';"''', shell=True, check=True)
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name} psql -U {self.user} -h {self.host} -c "DROP DATABASE IF EXISTS {self.db_name_temp};"', shell=True, check=True)
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name} psql -U {self.user} -h {self.host} -c "CREATE DATABASE {self.db_name_temp};"', shell=True, check=True)
    
        #Create extensions
        subprocess.run(F'PGPASSFILE=~/.pgpass_{self.db_name_temp} psql -U {self.user} -h {self.host} -d {self.db_name_temp} -c "CREATE EXTENSION postgis;CREATE EXTENSION pgrouting;CREATE EXTENSION hstore;CREATE EXTENSION intarray;CREATE EXTENSION plpython3u;"', shell=True, check=True)
        subprocess.run(F'PGPASSFILE=~/.pgpass_{self.db_name_temp} psql -U {self.user} -h {self.host} -d {self.db_name_temp} -c "CREATE EXTENSION arraymath;CREATE EXTENSION floatvec;"', shell=True, check=True)

        #These extensions are needed when using the new DB-image
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name_temp} psql -U {self.user} -h {self.host} -d {self.db_name_temp} -c "CREATE EXTENSION postgis_raster;"', shell=True, check=True)
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name_temp} psql -U {self.user} -h {self.host} -d {self.db_name_temp} -c "CREATE EXTENSION plv8;"', shell=True, check=True)

        #Create user for renaming database later
        cmd = f'''PGPASSFILE=~/.pgpass_{self.db_name} psql -U {self.user} -h {self.host} -c "SELECT 1 FROM pg_roles WHERE rolname='{self.user+'empty'}';"'''
        cmd_return = subprocess.check_output(cmd, shell=True)
        
        if ('0 row' in str(cmd_return)): 
            subprocess.run(f'''PGPASSFILE=~/.pgpass_{self.db_name} psql -U {self.user} -h {self.host} -c "CREATE USER goatempty WITH password '{self.password}'; ALTER USER goatempty SUPERUSER;"''', shell=True, check=True)
    
        subprocess.run(f'''PGPASSFILE=~/.pgpass_{self.db_name} psql -U {self.user} -h {self.host} -c "DROP DATABASE IF EXISTS goatempty;"''', shell=True, check=True)
        subprocess.run(f'''PGPASSFILE=~/.pgpass_{self.db_name} psql -U {self.user} -h {self.host} -c "CREATE DATABASE goatempty;"''', shell=True, check=True)
        
        #Load PLV8 modules inside the database 
        subprocess.run(f'psql -U {self.user} -d {self.db_name_temp} -c "DROP TABLE IF EXISTS plv8_js_modules;"', shell=True, check=True)
        subprocess.run(f'psql -U {self.user} -d {self.db_name_temp} -f /opt/database_functions/libs/plv8_js_modules.sql', shell=True, check=True)
        subprocess.run(f'psql -U {self.user} -d {self.db_name_temp} -c "ALTER DATABASE {self.db_name_temp} SET plv8.start_proc TO plv8_require"', shell=True, check=True)


    def rename_databases(self):
        subprocess.run(f'''PGPASSFILE=~/.pgpass_{self.db_name} psql -U {self.user} -h {self.host} -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{self.db_name+'old'}';"''', shell=True, check=True)
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name} psql -U {self.user} -h {self.host} -c "DROP DATABASE IF EXISTS {self.db_name}old;"', shell=True, check=True)
        subprocess.run(f'''PGPASSFILE=~/.pgpass_{self.db_name}empty psql -U {self.user}empty -h {self.host} -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{self.db_name}';"''', shell=True, check=True)

        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name}empty psql -U {self.user}empty -h {self.host} -c "ALTER DATABASE {self.db_name} RENAME TO {self.db_name}old;"', shell=True, check=True)
        subprocess.run(f'''PGPASSFILE=~/.pgpass_{self.db_name}empty psql -U {self.user}empty -h {self.host} -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{self.db_name_temp}';"''', shell=True, check=True)
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name}empty psql -U {self.user}empty -h {self.host} -c "ALTER DATABASE {self.db_name_temp} RENAME TO {self.db_name};"', shell=True, check=True)
         
    def create_pgpass_files(self):
        self.read_yaml_config.create_pgpass('',self.user)
        self.read_yaml_config.create_pgpass('temp',self.user)
        self.read_yaml_config.create_pgpass('empty',self.user+'empty')


class FileHelper():
    """Some helper functions to read through data directories."""
    @staticmethod
    def list_files_dir(filepath, ending):
        file_list = []
        for filename in os.listdir(filepath):
            if filename.endswith(ending):
                file_list.append(filename)
    
        return file_list

    @staticmethod
    def list_files_for_import(filenames, ending_priority, table_names=[]):
        if table_names == []: 
            filenames = list(filter(lambda f: f.split('.')[0], filenames))
        else: 
            filenames = list(filter(lambda f: f.split('.')[0] in table_names, filenames))
        
        cleaned_list = []
        for filename in filenames: 
            if filename.endswith(ending_priority): 
                cleaned_list.append(filename)
            elif not filename.endswith(ending_priority) and filename.split('.')[0] + ending_priority not in filenames:
                cleaned_list.append(filename)

        return cleaned_list

class DataImport():
    """Functions to import data."""
    def __init__(self, read_yaml_config, is_temp, db_conn):
        self.goat_conf = read_yaml_config.return_goat_conf()
        self.db_conf = read_yaml_config.return_db_conf()
        self.db_name = self.db_conf["DB_NAME"]
        self.user = self.db_conf["USER"]
        self.host = self.db_conf["HOST"]
        self.folder_files = FileHelper().list_files_dir("/opt/data", ('.shp','.sql','.tif', 'json', 'geojson'))
        self.mandatory_data = self.goat_conf['DATA_IMPORT']['MANDATORY']
        self.optional_data = self.goat_conf['DATA_IMPORT']['OPTIONAL']
        self.goat_srid = self.goat_conf['DATA_IMPORT']['SRID']
        self.study_area = ''
        self.study_area_name = ''
        self.not_listed_shp = []

        for shp in self.folder_files:
            if (shp not in self.mandatory_data and shp not in self.optional_data):
                self.not_listed_shp.append(shp)
            else:
                pass

        if is_temp == True: 
            self.db_name = self.db_name + 'temp'

        self.download_link = read_yaml_config.return_goat_conf()["DATA_SOURCE"]["OSM_DOWNLOAD_LINK"]
        self.buffer = float(read_yaml_config.return_goat_conf()["DATA_SOURCE"]["BUFFER_BOUNDING_BOX"])
        self.extract_bbox = read_yaml_config.return_goat_conf()["DATA_SOURCE"]["EXTRACT_BBOX"]
        self.db_conn = db_conn
        
    def check_study_area(self):
        os.chdir('/opt/data')
        study_area_files = []
        for study_file in self.mandatory_data:
            if (study_file in self.folder_files):
                study_area_files.append(study_file)
        if (len(study_area_files) == 0):
            return GoatMessages().messages("error", "Study are file not detected. Please, insert a study area in sql, json or shp format")
        if (len(study_area_files) == 1):
            self.study_area = study_area_files[0]
            self.study_area_name = study_area_files[0]
            if(study_area_files[0].endswith('sql')):
                return GoatMessages().messages("info", "SQL File from Study Area Detected.") 
            if(study_area_files[0].endswith(('geojson', 'json'))):
                GoatMessages().messages("info", "GeoJSON File from Study Area Detected.")
                with open(study_area_files[0]) as g:
                    try:
                        geojson = json.load(g)
                        if not (geojson["features"][0]["properties"]):
                            return GoatMessages().messages("error", "There is no properties in the file. Please, update your Study Area File and try again.") 
                    except ValueError as e:
                        return GoatMessages().messages("error", "Your GeoJSON is not formatted correctly. Please, update your Study Area File and try again.") 
            if(study_area_files[0].endswith('.shp')):
                self.study_area = gpd.read_file(study_area_files[0])
                if(str(self.study_area.crs).split(':')[1] == '4326'):
                    return GoatMessages().messages("info", "{0} detected. Continue.".format(self.study_area.crs)) 
                else:
                    old_srid = str(self.study_area.crs)
                    self.study_area = self.study_area.to_crs(self.goat_srid)
                    self.study_area.to_file('study_area.shp')
                    return GoatMessages().messages("Converted from {0} => {1}".format(old_srid, self.goat_srid))
        if (len(study_area_files) > 1):
            return GoatMessages().messages("error", "You have more than one study area in supported formats. Please, use only one file")
  
    def check_study_area_schema(self):
        os.chdir('/opt/data')
        if (self.study_area_name.endswith('.shp')):
            layer = fiona.open(self.study_area_name)
            mandatory_fields = []
            if (layer.schema['geometry'] == 'Polygon'):
                for (key) in layer.schema['properties']:
                    if (key == 'name' and layer.schema['properties'][key].split(':')[0] == 'str'):
                        mandatory_fields.append({key: layer.schema[key]})
                    elif (key == 'sum_pop' and layer.schema['properties'][key].split(':')[0] == 'int'):
                        mandatory_fields.append({key: layer.schema['properties'][key]})
            if (len(mandatory_fields) < 2):
                return GoatMessages().messages("error", "Please, check the name from shapefile fields")
            elif (len(mandatory_fields) >= 2):
                return GoatMessages().messages("info", "Field validation passed.")
            else: 
                return GoatMessages().messages("error", "Geometry type: {0}. Please use a shapefile with Polygon geometry type".format(layer.schema['geometry']))
        if(self.study_area_name.endswith(('.geojson', 'json'))):
            with open(self.study_area_name) as g:
                geojson = json.load(g)
                if (("name"  and "sum_pop") in geojson["features"][0]["properties"]):
                    if (type(geojson["features"][0]["properties"]["name"]) == str and type(geojson["features"][0]["properties"]["sum_pop"]) == int):
                        return GoatMessages().messages("info", "You GeoJSON file has the right attributes. The process will continue.") 
                else:
                    return GoatMessages().messages("error", "Your properties are incomplete. Please, update your Study Area File and try again.") 

    def check_shp_srid(self):
        os.chdir('/opt/data')
        optional_files = []
        for shp in self.optional_data:
            if (shp in self.folder_files):
                optional_files.append(shp)

        for optional_shp in optional_files:
            optional_shp_file = gpd.read_file(optional_shp)
            if(str(optional_shp_file.crs).split(':')[1] == '4326'):
                GoatMessages().messages("info", "{0} detected in {1}. Continue.".format(optional_shp_file.crs, optional_shp)) 
            else:
                old_srid = str(optional_shp_file.crs)
                optional_shp_file = optional_shp_file.to_crs(self.goat_srid)
                optional_shp_file.to_file('{0}.shp'.format(optional_shp))
                GoatMessages().messages("info", "Converted from {0} => {1}".format(old_srid, self.goat_srid))

    def check_shp_schema(self):
        os.chdir('/opt/data')
        optional_files = []
        census_mandatory_fields = []
        landuse_mandatory_fields = []
        for shp in self.optional_data:
            if (shp in self.folder_files):
                optional_files.append(shp)
        for shp in optional_files:
            layer = fiona.open(shp)
            if (shp == 'census.shp'):
                for (key) in layer.schema['properties']:
                    print(layer.schema['properties']['id'])
                    if (key == 'id' and layer.schema['properties'][key].split(':')[0] == 'str'):
                        census_mandatory_fields.append({key: layer.schema['properties'][key]})
                    if (key == 'demography' and layer.schema['properties'][key].split(':')[0] == 'str'):
                        census_mandatory_fields.append({key: layer.schema['properties'][key]})
                    if (key == 'pop' and layer.schema['properties'][key].split(':')[0] == 'int'):
                        census_mandatory_fields.append({key: layer.schema['properties'][key]})
            if (shp == 'landuse.shp'):
                for (key) in layer.schema['properties']:
                    if (key == 'landuse' and layer.schema['properties'][key].split(':')[0] == 'str'):
                        landuse_mandatory_fields.append({key: layer.schema['properties'][key]})
        if (len(census_mandatory_fields) < 3):
            GoatMessages().messages("warning", "Your census shapefile do not have all mandatory fields.")
        elif (len(landuse_mandatory_fields) < 1):
            GoatMessages().messages("warning", "Your land use shapefile do not have all mandatory fields.")
        else: 
            GoatMessages().messages("info", "All optional shapefiles has the right fields structure.")


    def prepare_planet_osm(self):
        os.chdir('/opt/data') 
        if self.download_link != 'no_download':     
            print('Fresh OSM-data will be download from: %s' % self.download_link)
            result = subprocess.run(f'wget --no-check-certificate --output-document="raw-osm.osm.pbf" {self.download_link}', shell=True, check=True)

            if result.returncode != 0:
                return {"Error": "Download not successful"}

        if self.extract_bbox == "yes":
            print('###########################OSM-Data will be clipped###########################')
            self.db_conn.perform(open('/opt/database_functions/data_preparation/other/create_bbox_study_area.sql', "r").read())
            bboxes = self.db_conn.select('SELECT * FROM create_bbox_study_area(%(buffer)s)', params={"buffer":self.buffer})[0][0]
            subprocess.run(f'osmosis --read-pbf file="raw-osm.osm.pbf" {bboxes} --write-xml file="study_area.osm"', shell=True, check=True)
        elif self.extract_bbox == "no_extract":
            print('#################All OSM-data from dump will be imported######################')
            subprocess.run(f'osmosis --read-pbf file="raw-osm.osm.pbf" --write-xml file="study_area.osm"', shell=True, check=True)
        elif self.extract_bbox == "done":
            print('###################All OSM-data was alread clipped############################')

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
            subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name} psql -d %s -U %s -h %s -f %s -q' % (self.db_name,self.user,self.host,filepath), shell=True, check=True) 
        elif data_type == 'tif':
            sql_path = filepath.replace('.tif','.sql')
            subprocess.run(f'raster2pgsql -c -C -s 4326 -f rast -F -I -M -t 100x100 {filepath} public.{table_name} > {sql_path}', shell=True, check=True)
            subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name} psql -d %s -U %s -h %s -f %s -q' % (self.db_name,self.user,self.host,sql_path), shell=True, check=True) 
        else:
            return 

    def import_data_folder(self,path_data):
        all_files = FileHelper().list_files_dir(path_data, ('.shp','.sql','.tif', 'json'))
        cleaned_files = FileHelper().list_files_for_import(all_files,'.sql')

        for f in cleaned_files:
            self.import_raw_layer(path_data + f)

    def find_newest_dump(self, namespace):
        fnames = []
        backup_path = "/opt/backups"
        for file in os.listdir(backup_path):
            if file.endswith(".sql") and namespace == file.split('_')[0]:
                fnames.append(file)
        newest_file = sorted(fnames)[-1]

        return os.path.join(backup_path, newest_file)

    def restore_db(self,filepath):
        #newest_file = find_newest_dump(namespace)
        #Drop backup db tags as old DB
        subprocess.run('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % (self.db_name+'old'), shell=True, check=True)
        subprocess.run('psql -U postgres -c "DROP DATABASE IF EXISTS %s;"' % (self.db_name+'old'), shell=True, check=True)
        subprocess.run('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % (self.db_name+'temp'), shell=True, check=True)
        subprocess.run('psql -U postgres -c "DROP DATABASE IF EXISTS %s;"' % (self.db_name+'temp'), shell=True, check=True)
        #Restore backup as temp db
        subprocess.run("psql -U postgres -c 'CREATE DATABASE %s;'"% (self.db_name+'temp'), shell=True, check=True)
        subprocess.run('psql -U %s -d %s -f %s' % (self.user,self.db_name+'temp',filepath), shell=True, check=True)
        #Rename active database into old DB
        subprocess.run('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % self.db_name, shell=True, check=True)
        subprocess.run('psql -U postgres -c "ALTER DATABASE %s RENAME TO %s;"' % (self.db_name,self.db_name+'old'), shell=True, check=True)
        #Rename temp DB into active db
        subprocess.run('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % (self.db_name+'temp'), shell=True, check=True)
        subprocess.run('psql -U postgres -c "ALTER DATABASE %s RENAME TO %s;"' % (self.db_name+'temp',self.db_name), shell=True, check=True)

class GoatMessages():
    logging.basicConfig(filename="/opt/data/setup_log.txt",
                    level=logging.INFO,
                    format='%(levelname)s: %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')

    def __init__(self) -> None:
        pass

    def messages(self, level, message):
        """
        Custom function to return messages in the user terminal 
        and also save in log.txt file inside op/data folder
        """
        if (level == 'info'):
            logging.info("==== GOAT INFO: {0} ====".format(message))
            print("==== GOAT INFO: {0} ====".format(message))
        if (level == 'warning'):
            logging.warning("==== GOAT WARNING: {0} ====".format(message))
            print("==== GOAT WARNING: {0} ====".format(message))
        if (level == 'error'):
            logging.error("==== GOAT ERROR: {0} ====".format(message))
            print("==== GOAT ERROR: {0} ====".format(message))