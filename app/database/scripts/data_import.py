import subprocess
import os 
from psycopg2 import sql
import yaml 

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
        self.db_conf = read_yaml_config.return_db_conf()
        self.db_name = self.db_conf["DB_NAME"]
        self.user = self.db_conf["USER"]
        self.host = self.db_conf["HOST"]
        if is_temp == True: 
            self.db_name = self.db_name + 'temp'

        self.download_link = read_yaml_config.return_goat_conf()["DATA_SOURCE"]["OSM_DOWNLOAD_LINK"]
        self.buffer = float(read_yaml_config.return_goat_conf()["DATA_SOURCE"]["BUFFER_BOUNDING_BOX"])
        self.extract_bbox = read_yaml_config.return_goat_conf()["DATA_SOURCE"]["EXTRACT_BBOX"]
        self.db_conn = db_conn

    def prepare_planet_osm(self):
        os.chdir('/opt/data') 
        if self.download_link != 'no_download' and self.extract_bbox != "done":     
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
        all_files = FileHelper().list_files_dir(path_data, ('.shp','.sql','.tif'))
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