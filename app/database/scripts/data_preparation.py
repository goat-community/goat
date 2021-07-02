import subprocess, json, os
from scripts.db.db import Database
class PrepareDatabase():
    """A couple of functions that help to prepare the GOAT database."""
    def __init__(self, read_yaml_config, is_temp, db_conn):
        self.db_conf = read_yaml_config.return_db_conf()
        self.db_name = self.db_conf["DB_NAME"]
        self.user = self.db_conf["USER"]
        self.host = self.db_conf["HOST"]
        if is_temp == True: 
            self.db_name = self.db_name + 'temp'

        self.mapping_conf = read_yaml_config.return_mapping_conf()
        self.data_refinement = read_yaml_config.return_goat_conf()["DATA_REFINEMENT_VARIABLES"]
        self.db_conn = db_conn

    def create_variable_container(self):
        self.db_conn.perform('''DROP TABLE IF EXISTS variable_container;
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
            self.db_conn.perform(sql_insert)

    def execute_script_psql(self,script):
        subprocess.run(f'PGPASSFILE=~/.pgpass_{self.db_name} psql -d {self.db_name} -U {self.user} -h {self.host} -f {script}', shell=True, check=True) 

    def execute_bulk_sql(self, directory):
        for root, dirs, files in os.walk(directory):
            for name in files:
                if name.endswith(".sql"): 
                    self.execute_script_psql(os.path.join(root, name))

    def create_functions(self):
        self.db_conn.perform(open('/opt/data_preparation/SQL/types.sql', "r").read())
        for p in ['/opt/database_functions/other','/opt/database_functions/network','/opt/database_functions/routing','/opt/database_functions/heatmap','/opt/database_functions/data_preparation', '/opt/database_functions/layers_api']:
            self.execute_bulk_sql(p)

    def data_preparation_table_types_functions(self):
        self.execute_script_psql('/opt/data_preparation/SQL/create_tables.sql')
        self.create_variable_container()
        self.execute_script_psql('/opt/data_preparation/SQL/types.sql')
        self.execute_bulk_sql('/opt/database_functions/data_preparation/essential_helpers')
        self.execute_bulk_sql('/opt/database_functions/data_preparation')

class Profiles:
    def __init__(self, db_suffix, ways_table, filter_ways):

        self.db_suffix = db_suffix
        db = Database(self.db_suffix)
        self.ways_table = ways_table
        self.filter_ways = filter_ways
        self.batch_size = 200
        self.elevs_interval = 25

        conn = db.connect()
        cur = conn.cursor()
        
        cur.execute('''SELECT count(*) FROM {0} {1};'''.format(self.ways_table, self.filter_ways))
        self.total_cnt = cur.fetchall()[0][0]
        
        cur.execute('''SELECT select_from_variable_container_s('one_meter_degree');''')
        self.meter_degree = float(cur.fetchall()[0][0])

        cur.execute('''SELECT id FROM {0} {1};'''.format(self.ways_table, self.filter_ways))
        ids = cur.fetchall()
        self.ids = [x[0] for x in ids]

        conn.close()
        
        
    def elevation_profile(self): 
        db = Database(self.db_suffix)
        conn = db.connect() 
        cur = conn.cursor()

        sql_create_table = '''
            DROP TABLE IF EXISTS elevs_{0};
            CREATE TABLE elevs_{0} 
            (
                id bigint,
                elevs float[],
                elevs_interval float,
                length_m float
            );'''.format(self.ways_table)
        cur.execute(sql_create_table)
        conn.commit()
 
        cnt = 0
        for i in self.ids:         
            cnt = cnt + 1 
            if (cnt/self.batch_size).is_integer():
                print('Slope profile for %s out of %s lines' % (cnt,self.total_cnt)) 
                conn.commit()

            sql_elevs = '''
            INSERT INTO elevs_{0}(id, elevs, elevs_interval, length_m)
            WITH way AS 
            (
                SELECT id, geom, length_m
                FROM {0}
                WHERE id = {1}
            )
            SELECT w.id, s.elevs, {2} elevs_interval, w.length_m
            FROM way w, 
            LATERAL (
                SELECT ARRAY_AGG(elev) elevs
                FROM get_elevation_profile_vector(geom, length_m, {3}, {2})
            ) s;'''.format(self.ways_table, i, self.elevs_interval, self.meter_degree)

            cur.execute(sql_elevs)

        conn.commit()

        sql_null_false = '''UPDATE elevs_{0} 
            SET elevs = NULL 
            WHERE ARRAY_LENGTH(elevs,1) = 1
        '''.format(self.ways_table)
        cur.execute(sql_null_false)

        cur.execute('ALTER TABLE elevs_{0} ADD PRIMARY KEY (id);'.format(self.ways_table))
        conn.commit() 
        conn.close()

    def compute_cycling_impedance(self):
        db = Database(self.db_suffix)
        conn = db.connect() 
        cur = conn.cursor()
        sql_create_table = '''
            DROP TABLE IF EXISTS impedances_{0};
            CREATE TABLE impedances_{0} 
            (
                id bigint,
                s_imp float,
                rs_imp float
            );'''.format(self.ways_table)
        cur.execute(sql_create_table)
        conn.commit()

        cnt = 0
        for i in self.ids:         
            cnt = cnt + 1 
            if (cnt/self.batch_size).is_integer():
                print('Compute impedances for %s out of %s lines' % (cnt,self.total_cnt)) 
                conn.commit()
            sql_update_impedance = '''
                INSERT INTO impedances_{0}(id, s_imp, rs_imp)
                SELECT x.id, i.imp, i.rs_imp
                FROM (
                    SELECT * 
                    FROM elevs_{0} 
                    WHERE id = {1}
                    AND elevs IS NOT NULL 
                ) x, LATERAL compute_impedances(elevs, length_m, elevs_interval)  i'''.format(self.ways_table, i)
            cur.execute(sql_update_impedance)

        conn.commit()    
        sql_primary_key = 'ALTER TABLE impedances_{0} ADD PRIMARY KEY (id);'.format(self.ways_table)
        cur.execute(sql_primary_key)
        conn.commit()
        conn.close()
    
    def compute_average_slope(self):
        db = Database(self.db_suffix)
        conn = db.connect() 
        cur = conn.cursor()

        sql_create_table = '''
            DROP TABLE IF EXISTS average_slopes_{0};
            CREATE TABLE average_slopes_{0} 
            (
                id bigint,
                slope float
            );'''.format(self.ways_table)

        cur.execute(sql_create_table)
        conn.commit()
        cnt = 0
        for i in self.ids:         
            cnt = cnt + 1 
            if (cnt/self.batch_size).is_integer():
                print('Compute slopes for %s out of %s lines' % (cnt,self.total_cnt)) 
                conn.commit()

            sql_update_impedance = '''
                INSERT INTO average_slopes_{0}(id, slope)
                SELECT e.id, compute_average_slope(elevs, length_m, elevs_interval) 
                FROM (SELECT * FROM elevs_{0} WHERE id  = {1}) e'''.format(self.ways_table, i)

            cur.execute(sql_update_impedance)

        conn.commit()
        cur.execute('ALTER TABLE average_slopes_{0} ADD PRIMARY KEY (id);'.format(self.ways_table))
        conn.commit()
        conn.close()

    def create_export_table(self):
        db = Database(self.db_suffix)
        conn = db.connect() 
        cur = conn.cursor()
        
        sql_merge_tables = '''DROP TABLE IF EXISTS slope_profile_{0};   
        CREATE TABLE slope_profile_{0} AS 
        SELECT e.*, i.s_imp, i.rs_imp, s.slope, w.geom   
        FROM elevs_{0} e
        LEFT JOIN average_slopes_{0} s
        ON e.id = s.id
        LEFT JOIN impedances_{0} i 
        ON e.id = i.id 
        LEFT JOIN {0} w 
        ON e.id = w.id;'''.format(self.ways_table) 

        cur.execute(sql_merge_tables)
        cur.execute('ALTER TABLE slope_profile_{0} ADD PRIMARY KEY (id);'.format(self.ways_table))
        cur.execute('CREATE INDEX ON slope_profile_{0} USING GIST(geom);'.format(self.ways_table))
        conn.commit()
        conn.close()
    
    def update_line_tables(self):
        db = Database(self.db_suffix)
        conn = db.connect() 
        cur = conn.cursor()
        if self.ways_table == 'ways':
            sql_update = '''
                UPDATE ways w  
                SET s_imp = s.s_imp, rs_imp = s.rs_imp 
                FROM slope_profile_ways s 
                WHERE ST_EQUALS(w.geom, s.geom) 
            '''
        elif self.ways_table == 'footpaths_visualization': 
            sql_update = '''
                UPDATE footpath_visualization f
                SET incline_percent = slope 
                FROM slope_profile_footpath_visualization s 
                WHERE ST_EQUALS(f.geom, s.geom) 
            '''
        else:
            return {"Error": 'Please specify a valid table!'}
        
        cur.execute(sql_update)
        conn.commit()
        conn.close()

class PrepareLayers():
    """Data layers such as population as prepared with this class."""
    def __init__(self, read_yaml_config, is_temp, prepare_db, db_conn):
        self.read_yaml_config = read_yaml_config
        self.prepare_db = prepare_db
        self.db_conn = db_conn
        self.db_conf = read_yaml_config.return_db_conf()
        self.db_name = self.db_conf["DB_NAME"]
        self.user = self.db_conf["USER"]
        self.host = self.db_conf["HOST"]
        self.db_suffix = ''
        if is_temp == True: 
            self.db_name = self.db_name + 'temp'
            self.db_suffix = 'temp'

    def check_table_exists(self, table_name):
        return self.db_conn.select('''SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE  table_schema = 'public'
            AND    table_name   = %(table_name)s);''', params={"table_name": table_name})[0][0]

    def prepare_data(self, cls_import, cls_helper):
        raw_files = cls_helper.list_files_for_import(
            cls_helper.list_files_dir('/opt/data/', ('.shp','.sql')), '.sql',
            ['buildings_custom','population','study_area','landuse','landuse_additional','pois']
        )

        for f in raw_files:
            cls_import.import_raw_layer('/opt/data/'+f)

    def produce_population_points(self, source_population):
        print ('It was chosen to use population from: ', source_population)  
        self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/landuse_osm.sql')
        self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/population/data_fusion_buildings.sql')
        self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/population/classify_buildings.sql')
        self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/population/create_residential_addresses.sql')

        if source_population == 'census_standard':
            self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/population/prepare_census.sql')
            self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/population/population_census.sql')
        elif source_population == 'census_extrapolation':
            self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/population/prepare_census.sql')
            self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/population/population_extrapolated_census.sql')
        elif source_population == 'disaggregation':
            self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/population/population_disaggregation.sql')
        elif source_population == 'custom_population':
            #Some logic for checking custom population missing
            print('Custom population will be used.')
        else: 
            print('No valid population mode was provided. Therefore the population scripts cannot be executed.')

        self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/population/create_population_userinput.sql')

    def pois(self):
        self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/pois.sql')
    
    def ways(self):
        self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/network_preparation1.sql')
        vars_container = self.read_yaml_config.return_goat_conf()["DATA_REFINEMENT_VARIABLES"]["variable_container"]

        if vars_container["compute_slope_impedance"][1:-1] == 'yes':
            slope_profiles = Profiles(db_suffix=self.db_suffix, ways_table='ways', filter_ways='''WHERE class_id::text NOT IN(SELECT UNNEST(select_from_variable_container(\'excluded_class_id_cycling\')))''' )
            if self.check_table_exists('slope_profile_ways') == True: 
                slope_profiles.update_line_tables()
            else: 
                self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/prepare_dem.sql')
                slope_profiles.elevation_profile()
                slope_profiles.compute_cycling_impedance()
                slope_profiles.compute_average_slope()

        self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/network_preparation2.sql')

    def walkability(self):   
        if (self.read_yaml_config.return_goat_conf()["DATA_REFINEMENT_VARIABLES"]["ADDITIONAL_WALKABILITY_LAYERS"] == 'yes'):
            self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/layer_preparation.sql')
            self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/street_furniture.sql')

        if (self.read_yaml_config.return_goat_conf()["DATA_REFINEMENT_VARIABLES"]["WALKABILITY_INDEX"] == 'yes'):
            slope_profiles = Profiles(db_suffix=self.db_suffix, ways_table='footpath_visualization', filter_ways='')
            slope_profiles.update_line_tables()
            self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/walkability.sql')

    def mapping_tables(self):
        if (self.read_yaml_config.return_goat_conf()["DATA_REFINEMENT_VARIABLES"]["OSM_MAPPING_FEATURE"] == 'yes'):
            self.prepare_db.execute_script_psql('/opt/data_preparation/SQL/create_tables_mapping.sql')
    
    def insert_osm_timestamp(self):
        import datetime 
        from datetime import timedelta
        timestamp = str(datetime.datetime.now().date()-timedelta(days=1))
        self.db_conn.perform('''INSERT INTO variable_container(identifier, variable_simple) VALUES ('data_recency',%(timestamp)s)''', params={"timestamp":timestamp})

