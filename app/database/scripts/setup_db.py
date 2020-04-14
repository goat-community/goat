#!/usr/bin/env python3
# -*- coding: utf-8 -*-
def setup_db(setup_type):
    #Read Configuration
    import shapefile
    import os, glob, os.path
    import datetime,psycopg2
    from datetime import timedelta

    from scripts.db_functions import ReadYAML
    from scripts.db_functions import DB_connection
    from scripts.db_functions import create_variable_container
    from scripts.db_functions import update_functions

    download_link,osm_data_recency,buffer,extract_bbox,source_population,additional_walkability_layers = ReadYAML().data_source()
    db_name,user,host,port,password = ReadYAML().db_credentials()
    db_name_temp = db_name+'temp'

    db_temp = DB_connection(db_name_temp,user,host)

   
    #Create temporary database
    os.system('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % db_name_temp)
    os.system('psql -U postgres -c "DROP DATABASE IF EXISTS %s;"' % db_name_temp)
    os.system('psql -U postgres -c "CREATE DATABASE %s;"' % db_name_temp)
    #Create pgpass-file for temporary database
    ReadYAML().create_pgpass('temp')
    #Create extensions
    os.system('psql -U postgres -d %s -c "CREATE EXTENSION postgis;CREATE EXTENSION pgrouting;CREATE EXTENSION hstore;CREATE EXTENSION intarray;CREATE EXTENSION plpython3u;"' % db_name_temp)

    #These extensions are needed when using the new DB-image
    #os.system('psql -U postgres -d %s -c "CREATE EXTENSION postgis_raster;"' % db_name_temp)
    #os.system('psql -U postgres -d %s -c "CREATE EXTENSION plv8;"' % db_name_temp)
    os.chdir('/opt/data')


    if (download_link != 'no_download' and setup_type == 'new_setup'):
        os.system('wget --no-check-certificate --output-document="raw-osm.osm.pbf" %s' % download_link)
     
    #Define bounding box, the boundingbox is buffered by approx. 3 km
    bbox = shapefile.Reader("study_area.shp").bbox
    top = bbox[3]+buffer
    left = bbox[0]-buffer
    bottom = bbox[1]-buffer
    right = bbox[2]+buffer

    if (setup_type == 'new_setup'):  
        if (extract_bbox == 'yes'):
            bounding_box = '--bounding-box top=%f left=%f bottom=%f right=%f' % (top,left,bottom,right)
            print('Your bounding box is: ' + bounding_box)
            os.system('osmosis --read-pbf file="raw-osm.osm.pbf" %s --write-xml file="study_area.osm"' % bounding_box)

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
        if os.path.isfile('dem.tif'):
            #os.system('gdalwarp -dstnodata -999.0 -r near -ot Float32 -of GTiff -te %f %f %f %f dem.tif dem_cut.tif' % (left,top,right,bottom))
            os.system('raster2pgsql -c -C -s 4326 -f rast -F -I -M -t 100x100 dem.tif public.dem > dem.sql')
            db_temp.execute_script_psql('dem.sql')
            db_temp.execute_script_psql('/opt/data_preparation/SQL/prepare_dem.sql')
        #Import shapefiles into database
        for file in glob.glob("*.shp"):
            print(file)
            os.system('PGPASSFILE=/.pgpass shp2pgsql -I -s 4326  %s public.%s | PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -q' % (file,file.split('.')[0],db_name_temp,user,host))
            

    #Use OSM-Update-Tool in order to fetch the most recent data
    if (osm_data_recency == 'most_recent'):
        #Take last timestamp
        file = open('timestamps.txt','r')
        for line in file:
            pass
        timestamp=str(line.replace('\n',''))
        print('You are fetching the most recent changes from OSM.')
        os.system('osmupdate study_area.osm %s study_area_update.osm -b=%f,%f,%f,%f' % (timestamp,left,bottom,right,top))

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
            os.system('pg_dump -U %s -d %s -t %s | psql -d %s -U %s' % (user,db_name,table_name,db_name_temp,user))


    #Create tables and types
    db_temp.execute_script_psql('/opt/data_preparation/SQL/create_tables.sql')
    db_temp.execute_text_psql(create_variable_container())
    db_temp.execute_script_psql('/opt/data_preparation/SQL/types.sql')
    #Create functions that are needed for data_preparation
    db_temp.execute_script_psql('/opt/database_functions/other/select_from_variable_container.sql')
    db_temp.execute_script_psql('/opt/database_functions/network/split_long_way.sql')
    db_temp.execute_script_psql('/opt/database_functions/network/compute_slope.sql')
    db_temp.execute_script_psql('/opt/database_functions/network/slope_impedance.sql')

    if (setup_type in ['new_setup','all','population','pois','network']):
        os.system('PGPASSFILE=/.pgpass osm2pgsql -d %s -H %s -U %s --hstore -E 4326 study_area.osm' % (db_name_temp,host,user)) 
        

    if (setup_type in ['new_setup','population','pois']):    
        os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name_temp,user,host,'../data_preparation/SQL/pois.sql'))
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

    if (setup_type in ['new_setup','all','network']):
        os.system('PGPASSFILE=/.pgpass osm2pgrouting --dbname %s --host %s --username %s --file "study_area.osm" --conf ../mapconfig.xml --clean' % (db_name_temp,host,user)) 
        db_temp.execute_script_psql('../data_preparation/SQL/network_preparation.sql')
        if (additional_walkability_layers == 'yes'):
            db_temp.execute_script_psql('../data_preparation/SQL/layer_preparation.sql')


    if (setup_type == 'new_setup'):    
        #Create pgpass for goat-database
        ReadYAML().create_pgpass('')  
        os.system('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % (db_name+'old'))
        os.system('psql -U postgres -c "DROP DATABASE %s;"' % (db_name+'old'))
        os.system('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % db_name)
        os.system('psql -U postgres -c "ALTER DATABASE %s RENAME TO %s;"' % (db_name,db_name+'old'))
        os.system('psql -U postgres -c "ALTER DATABASE %s RENAME TO %s;"' % (db_name_temp, db_name))
               
        #Creates DB_functions
        update_functions()
        #os.system(f'psql --U {user} -d {db_name} -f /opt/database_functions/libs/plv8_js_modules.sql')
        #os.system(f'psql -U {user} -d {db_name} -c "ALTER DATABASE {db_name} SET plv8.start_proc TO plv8_require')

    else:
        #Create pgpass for goat-database
        ReadYAML().create_pgpass('')
        con = psycopg2.connect("dbname='%s' user='%s' port = '%s' host='%s' password='%s'" % (
        db_name_temp, user, port, host, password))

        cursor = con.cursor()
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
        #Refresh all tables that have changed
        for table in tables_to_update:  
            table = table[0]
            if (table !=  'spatial_ref_sys'):
                os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -c "DROP TABLE %s CASCADE;"' % (db_name,user,host,table))
                os.system('pg_dump -U %s -d %s -t %s | psql -d %s -U %s' % (user,db_name_temp,table,db_name,user))

        os.system('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % db_name_temp)
        os.system('psql -U postgres -c "DROP DATABASE %s;"' % db_name_temp)
