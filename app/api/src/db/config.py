import os.path
import yaml


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
    print("no db config file!. Using env variables.")

# Config Database from db_dev or env variables. 
DATABASE_HOST = os.getenv('POSTGRES_HOST', default=db_conf["HOST"])
DATABASE_USERNAME = os.getenv('POSTGRES_USER', default=db_conf["USER"])
DATABASE_PASSWORD = os.getenv('POSTGRES_PASS', default=db_conf["PASSWORD"])
DATABASE_PORT = os.getenv('POSTGRES_PORT', default=db_conf["PORT"])
DATABASE_NAME = os.getenv('POSTGRES_DBNAME', default=db_conf["DB_NAME"])

DATABASE = {
    'user':     DATABASE_USERNAME,
    'password': DATABASE_PASSWORD,
    'host':     DATABASE_HOST,
    'port':     DATABASE_PORT,
    'dbname': DATABASE_NAME
}
