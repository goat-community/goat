import io
import os

from flask import Flask, request, make_response, send_file
from flask_restful import Api, Resource
from flask_cors import CORS

from utils import response
from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs, parser, abort

from utils.geo.mvt import MVT
from db.db import Database

# Create database class
db = Database()

app = Flask(__name__)
CORS(app)
api = Api(app)

class Layer(Resource):
    def __init__(self):
        self.metadata = db.select('''SELECT * FROM layer_metadata''')[0][0]
        self.mvt = MVT()

    def get(self, layer):
        arguments = request.args
        #Test values------------
        queryParams = {
            'amenities_json': '''{"nursery":{"sensitivity":250000,"weight":1}}''',
            'modus_input': 'default',
            'scenario_id_input': 1
        }

        tile = {
                "zoom": 2,
                "x": 2,
                "y": 2,
                "format": "pbf",
        }
        layer = queryParams.args['layer']
        #----------------------
        layer_config = self.metadata[layer]
        # Check if layer exists in db
        if not layer_config:
            return response.failure({
                'errors': {
                    'message': "The layer doesn't exist"
                }
            }, 400)
        # Get the env for the tile. 
        if not (tile and self.mvt.tileIsValid(tile)):
            return response.failure( {
                'errors': {
                    'message': "invalid tile path: %s" % (self.path)
                }
            },400)
            
        env = self.mvt.tileToEnvelope(tile)
        table = layer
        if layer_config == "function":
            table = '''(SELECT * FROM {table}({args}))'''

        tbl = {
            "env": self.mvt.envelopeToBoundsSQL(env),
            "geomColumn": layer_config["geom"],
            "attrColumns": layer_config["columns"],
            "srid": layer_config["srid"],
            "table": table
        }

        vtSql = self.mvt.toSQL(tbl)
        print(vtSql)
        pbf = db.fetch_one(vtSql)

        bytes = io.BytesIO(pbf)
        return send_file(bytes, mimetype='application/vnd.mapbox-vector-tile')


api.add_resource(Layer,
                 '/api/<string:layer>/'
                 )

# SERVER CONFIG
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
