#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def setup_db(setup_type):
    #Read Configuration
    import shapefile
    import os, glob, os.path
    import datetime,psycopg2
    from datetime import timedelta
    import sys
    import subprocess
    from scripts.db_functions import ReadYAML
    from scripts.db_functions import DB_connection
    from scripts.db_functions import create_variable_container
    from scripts.db_functions import update_functions
    from scripts.db_functions import geojson_to_sql
    from scripts.db_functions import bulk_compute_slope

    download_link,osm_data_recency,buffer,extract_bbox,source_population,additional_walkability_layers,osm_mapping_feature = ReadYAML().data_source()
    compute_slope_impedance = ReadYAML().data_refinement()["variable_container"]["compute_slope_impedance"]

    db_name,user,host,port,password = ReadYAML().db_credentials()
    db_name_temp = db_name+'temp'

    db_temp = DB_connection(db_name_temp,user,host,port,password)

    #Create pgpass-file for normal and temporary DB
    ReadYAML().create_pgpass('',user)
    ReadYAML().create_pgpass('temp',user)
    ReadYAML().create_pgpass('empty',user+'empty')

    #Create seperate user if not exists for renaming DBs afterwards
    cmd = f'''PGPASSFILE=~/.pgpass_{db_name} psql -U {user} -h {host} -c "SELECT 1 FROM pg_roles WHERE rolname='{user+'empty'}';"'''
    cmd_return = subprocess.check_output(cmd,shell=True)
    
    if ('0 row' in str(cmd_return)): 
        print(cmd_return)
        os.system(f'''PGPASSFILE=~/.pgpass_{db_name} psql -U {user} -h {host} -c "CREATE USER goatempty WITH password '{password}'; ALTER USER goatempty SUPERUSER;"''')
   
    os.system(f'''PGPASSFILE=~/.pgpass_{db_name} psql -U {user} -h {host} -c "DROP DATABASE IF EXISTS goatempty;"''')
    os.system(f'''PGPASSFILE=~/.pgpass_{db_name} psql -U {user} -h {host} -c "CREATE DATABASE goatempty;"''')
    
    #Create temporary database
    os.system(f'''PGPASSFILE=~/.pgpass_{db_name} psql -U {user} -h {host} -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{db_name_temp}';"''')
    os.system(f'PGPASSFILE=~/.pgpass_{db_name} psql -U {user} -h {host} -c "DROP DATABASE IF EXISTS {db_name_temp};"')
    os.system(f'PGPASSFILE=~/.pgpass_{db_name} psql -U {user} -h {host} -c "CREATE DATABASE {db_name_temp};"')
   
    #Create extensions
    os.system(F'PGPASSFILE=~/.pgpass_{db_name_temp} psql -U {user} -h {host} -d {db_name_temp} -c "CREATE EXTENSION postgis;CREATE EXTENSION pgrouting;CREATE EXTENSION hstore;CREATE EXTENSION intarray;CREATE EXTENSION plpython3u;"')

    #These extensions are needed when using the new DB-image
    os.system(f'PGPASSFILE=~/.pgpass_{db_name_temp} psql -U {user} -h {host} -d {db_name_temp} -c "CREATE EXTENSION postgis_raster;"')
    os.system(f'PGPASSFILE=~/.pgpass_{db_name_temp} psql -U {user} -h {host} -d {db_name_temp} -c "CREATE EXTENSION plv8;"')

    os.chdir('/opt/data')

    if (download_link != 'no_download' and setup_type == 'new_setup'):
        os.system(f'wget --no-check-certificate --output-document="raw-osm.osm.pbf" {download_link}')
     
    #Define bounding box, the boundingbox is buffered by approx. 3 km
    bbox = shapefile.Reader("study_area.shp").bbox
    top = bbox[3]+buffer
    left = bbox[0]-buffer
    bottom = bbox[1]-buffer
    right = bbox[2]+buffer

    if (setup_type == 'new_setup'):  
        if (extract_bbox == 'yes'):
            bounding_box = f'--bounding-box top={top} left={left} bottom={bottom} right={right}'
            print('Your bounding box is: ' + bounding_box)
            os.system(f'osmosis --read-pbf file="raw-osm.osm.pbf" {bounding_box} --write-xml file="study_area.osm"')

        #Create timestamps
        os.system('rm timestamps.txt')
        os.system('touch timestamps.txt')
        #Create timestamp by substracting one day (usually Geofabrik files are one day old)
        currentDT = datetime.datetime.now()-timedelta(days=1)
        timestamp = currentDT.strftime("%Y-%m-%d")+'T'+currentDT.strftime("%H:%M:%S")+'Z'
        print(timestamp)
        file = open("timestamps.txt","a")
        file.write(timestamp+'\n')
        file.close()

        #Import DEM
        if os.path.isfile('dem_vec.sql'):
            db_temp.execute_script_psql('dem_vec.sql')
        elif os.path.isfile('dem.tif'):
            #os.system('gdalwarp -dstnodata -999.0 -r near -ot Float32 -of GTiff -te %f %f %f %f dem.tif dem_cut.tif' % (left,top,right,bottom))
            os.system('raster2pgsql -c -C -s 4326 -f rast -F -I -M -t 100x100 dem.tif public.dem > dem.sql')
            db_temp.execute_script_psql('dem.sql')
            db_temp.execute_script_psql('/opt/data_preparation/SQL/prepare_dem.sql')

        #Import shapefiles into database
        for file in glob.glob("*.shp"):
            print(file)
            os.system(f'PGPASSFILE=~/.pgpass_{db_name_temp} shp2pgsql -I -s 4326  %s public.%s | PGPASSFILE=~/.pgpass_{db_name_temp} psql -d %s -U %s -h %s -q' % (file,file.split('.')[0],db_name_temp,user,host))
         
        #Import custom pois
        if glob.glob('custom_pois/*.geojson'):
            geojson_to_sql(db_name_temp,user,host,port,password)
            db_temp.execute_text_psql(f'DELETE FROM custom_pois WHERE NOT ST_INTERSECTS(geom,ST_MAKEENVELOPE({left},{bottom},{right},{top}, 4326))')
            
    #Use OSM-Update-Tool in order to fetch the most recent data
    if (osm_data_recency == 'most_recent'):
        #Take last timestamp
        file = open('timestamps.txt','r')
        for line in file:
            pass
        timestamp=str(line.replace('\n',''))
        print('You are fetching the most recent changes from OSM.')
        os.system(f'osmupdate study_area.osm {timestamp} study_area_update.osm -b={left},{bottom},{right},{top}')

        #Add new timestamp
        currentDT = datetime.datetime.now()
        timestamp = currentDT.strftime("%Y-%m-%d")+'T'+currentDT.strftime("%H:%M:%S")+'Z'
        print(timestamp)
        file = open('timestamps.txt','a')
        file.write(timestamp+'\n')
        file.close()
        os.system('mv study_area_update.osm study_area.osm')

    #Reduce files-size OSM-file
    os.system('osmconvert study_area.osm --drop-author --drop-version --out-osm -o=study_area_reduced.osm')
    os.system('rm study_area.osm | mv study_area_reduced.osm study_area.osm')

    #Copy custom data into temporary database

    if (setup_type in ['all','population','pois','network']):
        for file in glob.glob("*.shp"):
            table_name = file.split('.')[0]
            os.system(f'PGPASSFILE=~/.pgpass_{db_name} pg_dump -U {user} -d {db_name} -h {host} -t {table_name} | PGPASSFILE=~/.pgpass_{db_name_temp} psql -d {db_name_temp} -U {user} -h {host}')

    #Create tables and types
    db_temp.execute_script_psql('/opt/data_preparation/SQL/create_tables.sql')
    
    create_variable_container(db_name_temp,user,str(port),host,password)
    db_temp.execute_script_psql('/opt/data_preparation/SQL/types.sql')
    
    #Create functions that are needed for data_preparation
    for file in glob.glob('/opt/database_functions/data_preparation/*'):
        db_temp.execute_script_psql(file)

    if (setup_type in ['new_setup','all','population','pois','network']):
        os.system(f'PGPASSFILE=~/.pgpass_{db_name_temp} osm2pgsql -d {db_name_temp} -H {host} -U {user} --hstore -E 4326 study_area.osm') 
        

    if (setup_type in ['new_setup','population','pois']):    
        os.system(f"PGPASSFILE=~/.pgpass_{db_name_temp} psql -d {db_name_temp} -h {host} -U {user} -f {'../data_preparation/SQL/pois.sql'}")
        if (setup_type in ['new_setup','population']):
            print ('It was chosen to use population from: ', source_population)
            if os.path.isfile('buildings.shp'):
                script_buildings = 'buildings_residential_custom.sql'
            else:
                script_buildings = 'buildings_residential.sql'

            if (source_population == 'extrapolation'):
                db_temp.execute_script_psql('../data_preparation/SQL/'+script_buildings)
                db_temp.execute_script_psql('../data_preparation/SQL/census.sql')
            elif(source_population == 'disaggregation'):
                db_temp.execute_script_psql('../data_preparation/SQL/'+script_buildings)
                db_temp.execute_script_psql('../data_preparation/SQL/population_disagregation.sql')
            elif(source_population == 'distribution'):
                db_temp.execute_script_psql('../data_preparation/SQL/population_distribution.sql')

            db_temp.execute_script_psql('../data_preparation/SQL/create_population_userinput.sql')
    if (setup_type in ['new_setup','all','network']):
        os.system(f'PGPASSFILE=~/.pgpass_{db_name_temp} osm2pgrouting --dbname {db_name_temp} --host {host} --username {user} --file "study_area.osm" --conf ../mapconfig.xml --clean') 
        
        db_temp.execute_script_psql('../data_preparation/SQL/network_preparation1.sql')
        if compute_slope_impedance == 'yes':
            bulk_compute_slope(db_name_temp,user,port,host,password)
        db_temp.execute_script_psql('../data_preparation/SQL/network_preparation2.sql')

        if (additional_walkability_layers == 'yes'):
            db_temp.execute_script_psql('../data_preparation/SQL/layer_preparation.sql')
        if (osm_mapping_feature == 'yes'):
            db_temp.execute_script_psql('../data_preparation/SQL/create_tables_mapping.sql')

    if (setup_type == 'new_setup'):    
        os.system(f'''PGPASSFILE=~/.pgpass_{db_name} psql -U {user} -h {host} -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{db_name+'old'}';"''')
        os.system(f'PGPASSFILE=~/.pgpass_{db_name} psql -U {user} -h {host} -c "DROP DATABASE {db_name}old;"')
        os.system(f'''PGPASSFILE=~/.pgpass_{db_name}empty psql -U {user}empty -h {host} -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{db_name}';"''')
        
     
        os.system(f'PGPASSFILE=~/.pgpass_{db_name}empty psql -U {user}empty -h {host} -c "ALTER DATABASE {db_name} RENAME TO {db_name}old;"')
        os.system(f'PGPASSFILE=~/.pgpass_{db_name}empty psql -U {user}empty -h {host} -c "ALTER DATABASE {db_name_temp} RENAME TO {db_name};"')
               
        #Creates DB_functions
        update_functions()
        os.system(f'PGPASSFILE=~/.pgpass_{db_name} psql -U {user} -h {host} -d {db_name} -f /opt/database_functions/libs/plv8_js_modules.sql')

        #os.system(f'psql -U {user} -d {db_name} -c "ALTER DATABASE {db_name} SET plv8.start_proc TO plv8_require')

    else:
        con,cursor = db_temp.con_psycopg()

        #Select all tables that have changed
        sql_select_not_empty_tables = '''
        SELECT c.relname
        FROM pg_class c
        INNER JOIN pg_namespace n ON (n.oid = c.relnamespace)
        WHERE c.reltuples <> 0 AND c.relkind = 'r'
        AND nspname = 'public';
        '''
        cursor.execute(sql_select_not_empty_tables)
        tables_to_update = cursor.fetchall()
        con.close()
        #Refresh all tables that have changed
        for table in tables_to_update:  
            table = table[0]
            if (table !=  'spatial_ref_sys'):
                os.system(f'PGPASSFILE=~/.pgpass_{db_name} psql -d {db_name} -U {user} -h {host} -c "DROP TABLE {table} CASCADE;"')
                os.system(f'PGPASSFILE=~/.pgpass_{db_name_temp} pg_dump -U {user} -d {db_name_temp} -h {host} -t {table} | PGPASSFILE=~/.pgpass_{db_name} psql -d {db_name} -U {user} -h {host}')
        
        os.system(f'''PGPASSFILE=~/.pgpass_{db_name} psql -U {user} -h {host} -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{db_name_temp}';"''')
        os.system(f'PGPASSFILE=~/.pgpass_{db_name} psql -U {user} -h {host} -c "DROP DATABASE {db_name_temp};"')