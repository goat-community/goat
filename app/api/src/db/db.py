# Code based on https://github.com/hackersandslackers/psycopg2-tutorial/blob/master/psycopg2_tutorial/db.py
import logging as LOGGER
import psycopg2
from psycopg2 import sql
import geobuf
import geojson
import json
import geopandas as gpd
import shutil
import zipfile
from zipfile import ZipFile
import random
import os 
import io
from io import BytesIO
import os.path
import yaml

def database_config(db_suffix = ''):
       
    # EXAMPLE DB CONFIG
    db_conf = {
        'HOST': "db",
        'USER': "xxdbuserxx",
        'PASSWORD': "xxdbpasswordxx",
        'PORT': 5432,
        'DB_NAME': 'goat'
    }
    # LOAD db dev config if it exists
    try:
        with open(os.path.dirname(__file__) + "/../../../config/db/db_dev.yaml", 'r') as stream:
            db_conf = yaml.load(stream, Loader=yaml.FullLoader)
    except EnvironmentError:
        x = "Using env variables."
        #print("Using env variables.")

    # Config Database from db_dev or env variables. 
    DATABASE_HOST = os.getenv('POSTGRES_HOST', default=db_conf["HOST"])
    DATABASE_USERNAME = os.getenv('POSTGRES_USER', default=db_conf["USER"])
    DATABASE_PASSWORD = os.getenv('POSTGRES_PASS', default=db_conf["PASSWORD"])
    DATABASE_PORT = os.getenv('POSTGRES_PORT', default=db_conf["PORT"])
    DATABASE_NAME = os.getenv('POSTGRES_DBNAME', default=db_conf["DB_NAME"]) + db_suffix

  
    DATABASE = {
        'user':     DATABASE_USERNAME,
        'password': DATABASE_PASSWORD,
        'host':     DATABASE_HOST,
        'port':     DATABASE_PORT,
        'dbname': DATABASE_NAME
    }

    return DATABASE



class Database:
    """PostgreSQL Database class."""

    def __init__(self,db_suffix=''):
        self.conn = None
        self.db_suffix = db_suffix
    def connect(self):
        """Connect to a Postgres database."""
        if self.conn is None:
            try:
                connection_string = " ".join(("{}={}".format(*i) for i in database_config(self.db_suffix).items()))
                self.conn = psycopg2.connect(connection_string)
            except psycopg2.DatabaseError as e:
                LOGGER.error(e)
                raise e
            finally:
                LOGGER.info('Connection opened successfully.')
        return self.conn 
        
    def cur_execute(self, conn, cur, query, params=None, response=True):
        try:
            if params is None:             
                cur.execute(query)
            else:
                cur.execute(query, params)
        except Exception as e:
            conn.rollback()
            return type(e).__name__ #'Query was rolled back.'
        else:
            conn.commit()
            if response == True:
                return cur.fetchall()

    def perform(self, query, params=None):
        """Run a SQL query that does not return anything"""
        self.connect()
        with self.conn.cursor() as cur:            
            records = self.cur_execute(self.conn, cur, query, params=params,response=False)

        self.conn.commit()
        cur.close()

    def select(self, query, identifiers=None, params=None, return_type='raw'):
        """Run a SQL query and pass identifiers/params"""
        self.connect()
        with self.conn.cursor() as cur:
            if isinstance(query, str) == False:
                query = query
            elif identifiers is not None:
                query = sql.SQL(query).format(*map(sql.Identifier, identifiers))
            else: 
                query = sql.SQL(query)

            if return_type == 'geojson':
                
                sql_geojson =  [
                    sql.SQL('''SELECT jsonb_build_object(
                    'type',     'FeatureCollection',
                    'features', jsonb_agg(features.feature)
                    )
                    FROM (
                    SELECT jsonb_build_object(
                    'type',       'Feature',
                    'id',         gid,
                    'geometry',   ST_AsGeoJSON(geom)::jsonb,
                    'properties', to_jsonb(inputs) - 'geom' 
                    ) AS feature 
                    FROM ('''),
                    query,
                    sql.SQL('''    ) inputs ) features''')
                ]
                query = sql.SQL(' ').join(sql_geojson)

            if return_type in ['geobuf']:
                sql_geobuf = [
                    sql.SQL("SELECT ST_AsGeobuf(l, 'geom') FROM ("),
                    query,
                    sql.SQL(") l")
                ] 
                query = sql.SQL(' ').join(sql_geobuf)

            if return_type in ['raw','geobuf','geojson']:
                records = self.cur_execute(self.conn, cur, query, params=params)
                
            if return_type == 'geodataframe':
                records = gpd.GeoDataFrame.from_postgis(query, self.conn, geom_col='geom', params=params)

            if return_type in ['shapefile']:
                df = gpd.GeoDataFrame.from_postgis(query, self.conn, geom_col='geom', params=params)

                rand_number = str(random.randint(1,100000))
                dir_name = '/tmp/'+rand_number+'/'
                os.makedirs(dir_name)
                df.to_file(dir_name+'export.shp')

                shutil.make_archive('export_'+rand_number, 'zip', dir_name)

                with open('export_'+rand_number+'.zip', 'rb') as f:
                    data = f.readlines()
                               
                os.remove('export_'+rand_number+'.zip')
                shutil.rmtree(dir_name[0:len(dir_name)-1])
                records = data
        self.conn.commit()
        cur.close()
        return records 
    

    def perform_with_identifiers(self, query, identifiers=None, params=None):
        """Run a SQL query that does not return anything"""
        self.connect()

        if isinstance(query, str) == False:
            query = query
        elif identifiers is not None:
            query = sql.SQL(query).format(*map(sql.Identifier, identifiers))
        else: 
            query = sql.SQL(query)

        with self.conn.cursor() as cur:
            #prepared_query = sql.SQL(query).format(*map(sql.Identifier, identifiers))
            self.cur_execute(self.conn, cur, query, params=params, response=False)

        self.conn.commit()
        cur.close()

    def mogrify_query(self, query, params=None):
        """This will return the query as string for testing"""
        self.connect()
        with self.conn.cursor() as cur:
            if params is None:
                result = cur.mogrify(query)
            else:
                result = cur.mogrify(query, params)
        cur.close()
        return result
    
    def fetch_one(self, query, params=None):
        self.connect()
        with self.conn.cursor() as cur:
            try: 
                cur.execute(query)
            except Exception as e:
                conn.rollback()
                return type(e).__name__ 
            else:
                result = cur.fetchone()[0];
        cur.close()
        return result
        
    def cursor(self):
        """This will return the query as string for testing"""
        self.connect()
        self.conn.cursor()
        return self.conn.cursor()
