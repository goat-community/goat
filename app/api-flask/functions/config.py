import yaml

with open("../../config/db/db_dev.yaml", 'r') as stream:
    db_conf = yaml.load(stream, Loader=yaml.FullLoader)
        

# Config Database
DATABASE_HOST = db_conf["HOST"]
DATABASE_USERNAME = db_conf["USER"]
DATABASE_PASSWORD = db_conf["PASSWORD"]
DATABASE_PORT = db_conf["PORT"]
DATABASE_NAME = db_conf["DB_NAME"]