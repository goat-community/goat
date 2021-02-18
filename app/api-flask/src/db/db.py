# Code based on https://github.com/hackersandslackers/psycopg2-tutorial/blob/master/psycopg2_tutorial/db.py
import logging as LOGGER
import psycopg2
from db.config import DATABASE
from psycopg2 import sql
import geopandas as gpd
import json

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

    def select_with_identifiers(self, query, identifiers=None, params=None, return_type='raw'):
        """Run a SQL query and pass identifiers/params"""
        self.connect()
        with self.conn.cursor() as cur:

            if identifiers is not None:
                query = sql.SQL(query).format(*map(sql.Identifier, identifiers))
            
            if return_type == 'raw':
                if params is None:             
                    cur.execute(query)
                else:
                    cur.execute(query, params)
                records = cur.fetchall()
        
            if return_type in ['geodataframe', 'geojson']:
                if params is None:             
                    records = gpd.GeoDataFrame.from_postgis(query, self.conn, geom_col='geom')
                else:
                    records = gpd.GeoDataFrame.from_postgis(query, self.conn, geom_col='geom', params=params)
                
            if return_type == 'geojson':
                records = json.loads(records.to_json())

        self.conn.commit()
        cur.close()
        return records 
    
    def export_layer_geojson(self, sql_query, params=None):
        df = gpd.GeoDataFrame.from_postgis(sql_query, self.connect(), geom_col='geom', params=params)
        return json.loads(df.to_json())

    def export_layer_df(self, sql_query, params=None):
        df = gpd.GeoDataFrame.from_postgis(sql_query, self.connect(), geom_col='geom', params=params)
        self.conn.commit()
        return df

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
