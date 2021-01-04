# Code based on https://github.com/hackersandslackers/psycopg2-tutorial/blob/master/psycopg2_tutorial/db.py
import psycopg2
from log import LOGGER
from postgis import Point, LineString, Polygon
from postgis.psycopg import register


class Database:
    """PostgreSQL Database class."""

    def __init__(self):
        import yaml
        with open(os.path.dirname(__file__) + "/../../config/db/db_dev.yaml", 'r') as stream:
            db_conf = yaml.load(stream, Loader=yaml.FullLoader)

        self.host = db_conf["HOST"]
        self.username = db_conf["USER"]
        self.password = db_conf["PASSWORD"]
        self.port = db_conf["PORT"]
        self.dbname = db_conf["DB_NAME"]
        self.conn = None

    def connect(self):
        """Connect to a Postgres database."""
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password,
                    port=self.port,
                    dbname=self.dbname
                )
            except psycopg2.DatabaseError as e:
                LOGGER.error(e)
                raise e
            finally:
                LOGGER.info('Connection opened successfully.')

    def select(self, query, params=None):
        """Run a SQL query to select rows from table."""
        self.connect()
        with self.conn.cursor() as cur:
            if params is None:
                cur.execute(query)
            else:
                cur.execute(query, params)
            records = cur.fetchall()
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
        
    def cursor(self):
        """This will return the query as string for testing"""
        self.connect()
        self.conn.cursor()
        return self.conn.cursor()
