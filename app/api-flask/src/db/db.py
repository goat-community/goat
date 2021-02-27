# Code based on https://github.com/hackersandslackers/psycopg2-tutorial/blob/master/psycopg2_tutorial/db.py
import logging as LOGGER
import psycopg2
from db.config import DATABASE
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

class Database:
    """PostgreSQL Database class."""

    def __init__(self):
        self.conn = None

    def connect(self):
        """Connect to a Postgres database."""
        if self.conn is None:
            try:
                connection_string = " ".join(("{}={}".format(*i) for i in DATABASE.items()))
                self.conn = psycopg2.connect(connection_string)
            except psycopg2.DatabaseError as e:
                LOGGER.error(e)
                raise e
            finally:
                LOGGER.info('Connection opened successfully.')
        return self.conn 
        
    def select(self, query, params=None):
        """Run a SQL query to select rows from table."""
        self.connect()
        with self.conn.cursor() as cur:
            if params is None:
                cur.execute(query)
            else:
                cur.execute(query, params)
            records = cur.fetchall()
        
        self.conn.commit()
        cur.close()
        return records

    def perform(self, query, params=None):
        """Run a SQL query that does not return anything"""
        self.connect()
        with self.conn.cursor() as cur:
            if params is None:
                cur.execute(query)
            else:
                cur.execute(query, params)
        self.conn.commit()
        cur.close()

    def cur_execute(self, conn, cur, query, params=None):
        try:
            if params is None:             
                cur.execute(query)
            else:
                cur.execute(query, params)
        except Exception:
            conn.rollback()
            return 'Query was rolled back.'
        else:
            conn.commit()
            return cur.fetchall()


    def select_with_identifiers(self, query, identifiers=None, params=None, return_type='raw'):
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
    

    def perform_with_identifiers(self, query, identifiers, params=None):
        """Run a SQL query that does not return anything"""
        self.connect()
        with self.conn.cursor() as cur:
            prepared_query = sql.SQL(query).format(*map(sql.Identifier, identifiers))
            
            if params is None:               
                cur.execute(prepared_query)
            else:
                cur.execute(prepared_query, params)
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
            cur.execute(query)
            if not cur:
                self.send_error(404, "sql query failed: %s" % (query))
                return None
            else:
                result = cur.fetchone()[0];
        cur.close()
        return result
        
    def cursor(self):
        """This will return the query as string for testing"""
        self.connect()
        self.conn.cursor()
        return self.conn.cursor()
