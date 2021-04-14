
import os 
os.environ['POSTGRES_DBNAME'] = 'goattemp'
from db.db import Database
from db_functions import ReadYAML
from psycopg2 import sql

ReadYAML().create_pgpass('temp','goat')

db = Database()

def list_files_dir(filepath, ending):
    file_list = []
    for root, dirs, files in os.walk(filepath):
        for filename in files:
            if filename.endswith(ending):
                file_list.append(filename)
    return file_list

def list_files_for_import(filenames, ending_priority, table_names):
    filenames = list(filter(lambda f: f.split('.')[0] in table_names, filenames))
    
    cleaned_list = []
    for filename in filenames: 
        if filename.endswith(ending_priority): 
            cleaned_list.append(filename)
        elif not filename.endswith(ending_priority) and filename.split('.')[0] + ending_priority not in filenames:
            cleaned_list.append(filename)

    return cleaned_list

def import_raw_layer(filepath,db_conn,db_name,user,host):
    filename = os.path.basename(filepath) 
    data_type = filename.split('.')[1]
    table_name = filename.split('.')[0]

    print("The following file will be imported: %s" % filename)

    db_conn.perform(sql.SQL('DROP TABLE IF EXISTS {}').format(sql.Identifier(table_name)))
    if data_type == 'shp':
        os.system(f'PGPASSFILE=~/.pgpass_{db_name} shp2pgsql -I -s 4326  %s public.%s | PGPASSFILE=~/.pgpass_{db_name} psql -d %s -U %s -h %s -q' % (filepath,table_name,db_name,user,host))
    elif data_type == 'sql':
        #db_conn.perform(open(filepath, "r").read())
        os.system(f'PGPASSFILE=~/.pgpass_{db_name} psql -d %s -U %s -h %s -f %s -q' % (db_name,user,host,filepath))
    else:
        return 

def produce_population_points(db_conn,source_population):

    print ('It was chosen to use population from: ', source_population)

    raw_files = list_files_for_import(
        list_files_dir('/opt/data/', ('.shp','.sql')), '.sql',
        ['buildings','population','study_area','landuse','landuse_additional','pois']
    )

    for f in raw_files:
        import_raw_layer('/opt/data/'+f, db, 'goattemp', 'goat', 'db')

    db_conn.perform(open('/opt/data_preparation/SQL/landuse_osm.sql', "r").read())

    if db.select("SELECT * FROM to_regclass('public.buildings_custom')")[0][0] != None:
        #Data fusion of OSM building and custom buildings


        script_buildings = 'buildings_residential_custom.sql'
    else:
        script_buildings = 'buildings_residential.sql'

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

produce_population_points(db, 'extrapolation')

#os.environ['POSTGRES_DBNAME'] = 'goat'