import io

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
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
api = Api(app)


class Layer(Resource):
    def __init__(self):
        self.metadata = db.select('''SELECT * FROM layer_metadata''')[0][0]
        self.mvt = MVT()

    def get(self, layer, z, x, y):
        tile = {
            'zoom': z,
            'x': x,
            'y': y,
            'format': "pbf",
        }
        # ----------------------
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
            return response.failure({
                'errors': {
                    'message': "invalid tile path: %s" % (self.path)
                }
            }, 400)

        env = self.mvt.tileToEnvelope(tile)
        # Create table or function name

        table = layer
        if layer_config['layer_type'] == "function" and layer_config['args']:
            args = ""
            request_args = request.args.to_dict()
            for index, arg in enumerate(layer_config['args']):
                if not arg in request_args:
                    return response.failure({
                        'errors': {
                            'message': "Not all arguments available. "
                        }
                    })
                if index < len(layer_config['args']) - 1:
                    args += request_args[arg] + ","
                else:
                    args += request_args[arg]
            table = '''(SELECT * FROM {layer}({args}))'''.format(layer=layer, args=args)

        tbl = {
            'env': self.mvt.envelopeToBoundsSQL(env),
            'geomColumn': layer_config['geom'],
            'attrColumns': layer_config['columns'],
            'srid': layer_config['srid'],
            'table': table
        }

        vtSql = self.mvt.toSQL(tbl)
        pbf = db.fetch_one(vtSql)
        bytes = io.BytesIO(pbf)
        return send_file(bytes, mimetype='application/vnd.mapbox-vector-tile')

api.add_resource(Layer,
                 '/api/map/<string:layer>/<int:z>/<int:x>/<int:y>'
                 )

# SERVER CONFIG
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
