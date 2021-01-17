import yaml
import os.path

with open(os.path.dirname(__file__) + "/../../config/db/db_dev.yaml", 'r') as stream:
    db_conf = yaml.load(stream, Loader=yaml.FullLoader)


# Config Database
DATABASE_HOST = os.getenv('HOST', default=db_conf["HOST"])
DATABASE_USERNAME = os.getenv('USER', default=db_conf["USER"])
DATABASE_PASSWORD = os.getenv('PASSWORD', default=db_conf["PASSWORD"])
DATABASE_PORT = os.getenv('PORT', default=db_conf["PORT"])
DATABASE_NAME = os.getenv('DB_NAME', default=db_conf["DB_NAME"])

DATABASE = {
    'user':     db_conf["USER"],
    'password': db_conf["PASSWORD"],
    'host':     db_conf["HOST"],
    'port':     db_conf["PORT"],
    'dbname': db_conf["DB_NAME"]
}
