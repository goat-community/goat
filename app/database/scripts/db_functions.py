import yaml, os
class ReadYAML:
    with open("/opt/goat_config.yaml", 'r') as stream:
        conf = yaml.load(stream, Loader=yaml.FullLoader)
   
    db_conf = conf["DATABASE"]
    source_conf = conf["DATA_SOURCE"]
    refinement_conf = conf["DATA_REFINEMENT_VARIABLES"]

    def db_credentials(self):
        return self.db_conf["DB_NAME"],self.db_conf["USER"],self.db_conf["HOST"],self.db_conf["PORT"],self.db_conf["PASSWORD"]
    def data_source(self):
        return self.source_conf["OSM_DOWNLOAD_LINK"],self.source_conf["OSM_DATA_RECENCY"],self.source_conf["BUFFER_BOUNDING_BOX"],self.refinement_conf["POPULATION"]
    def data_refinement(self):
        return self.refinement_conf
    
class DB_connection:
    def __init__(self, db_name, user, host):
        self.db_name = db_name
        self.user = user
        self.host = host
    def execute_script_psql(self,script):
        os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (self.db_name,self.user,self.host,script))


def create_variable_container():
    variables = ReadYAML().data_refinement()
    print(variables)

create_variable_container()