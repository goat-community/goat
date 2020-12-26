import yaml
import os.path

with open(os.path.dirname(__file__) + "/../../config/db/db_dev.yaml", 'r') as stream:
    db_conf = yaml.load(stream, Loader=yaml.FullLoader)


# Config Database
DATABASE_HOST = db_conf["HOST"]
DATABASE_USERNAME = db_conf["USER"]
DATABASE_PASSWORD = db_conf["PASSWORD"]
DATABASE_PORT = db_conf["PORT"]
DATABASE_NAME = db_conf["DB_NAME"]

DATABASE = {
    'user':     db_conf["USER"],
    'password': db_conf["PASSWORD"],
    'host':     db_conf["HOST"],
    'port':     db_conf["PORT"],
    'database': db_conf["DB_NAME"]
}
