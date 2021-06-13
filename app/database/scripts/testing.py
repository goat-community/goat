import os 
from db.db import Database
from data_import import ReadYAML, CreateDatabase, DataImport, FileHelper
from data_preparation import PrepareDatabase, PrepareLayers

CreateDatabase(ReadYAML()).create_pgpass_files()
db_conn = Database()
data_import = DataImport(ReadYAML(), False, db_conn)
prepare_db = PrepareDatabase(ReadYAML(), False, db_conn)
prepare_layers = PrepareLayers(ReadYAML(), False, prepare_db, db_conn)

#data_import.load_js_lib()
#data_import.import_osm2pgrouting()
#prepare_layers.ways()

prepare_layers.walkability()



