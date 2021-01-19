import io
import os


from flask import Flask, request, send_file
from flask_restful import Api, Resource
from flask_cors import CORS
from utils import response

from resources.test_recompute import recompute_heatmap
from utils.geo.mvt import MVT
from db.db import Database
import config

db = Database()
app = Flask(__name__)
app.config.from_object(config.object_name[app.config['ENV']])
cors = CORS(app, resources={r"/v2/*": {"origins": "*"}})
api = Api(app)
PORT = os.getenv('APP_PORT', default=app.config['PORT'])

custom_methods_metadata = {
    'heatmap_geoserver': {
        'methodToCall': 'recomputed_heatmap',
        'methodArgs': ["scenario_id"]
    }
}


class Layer(Resource):
    def __init__(self):
        self.metadata = db.select('''SELECT * FROM layer_metadata''')[0][0]
        self.mvt = MVT()
        # Attach the custom logic method names and argumets to the existing metada
        for attr, value in custom_methods_metadata.items():
            if (self.metadata[attr]):
                self.metadata[attr].update(value)

    def get(self, layer, z, x, y):
        tile = {
            'zoom': z,
            'x': x,
            'y': y,
            'format': "pbf",
        }
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
        # Find table/function name. If there is a custom python logic to be executed before,
        # we should run it first. A metadata object will contain methodToCall and methodArgs
        # needed for the method call.
        request_args = request.args.to_dict()
        if (layer_config['methodToCall']):
            method_args = []
            for index, method_arg in enumerate(layer_config['methodArgs']):
                if not method_arg in request_args:
                    method_args = []
                    break
                method_args.append(request_args[method_arg])
            print(method_args)
            if len(method_args) > 0:
                recompute_heatmap(*method_args)

        table = layer
        if layer_config['layer_type'] == "function" and layer_config['args']:
            args = ""
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
            table = '''(SELECT * FROM {layer}({args}))'''.format(
                layer=layer, args=args)
        # Create the table object to pass in sql template string
        tbl = {
            'env': self.mvt.envelopeToBoundsSQL(env),
            'geomColumn': layer_config['geom'],
            'attrColumns': layer_config['columns'],
            'srid': layer_config['srid'],
            'table': table
        }
        # Create the sql string
        vtSql = self.mvt.toSQL(tbl)
        # Execute sql and send pbf back
        pbf = db.fetch_one(vtSql)
        bytes = io.BytesIO(pbf)
        return send_file(bytes, mimetype='application/vnd.mapbox-vector-tile')


api.add_resource(Layer,
                 '/v2/map/<string:layer>/<int:z>/<int:x>/<int:y>'
                 )

# SERVER CONFIG
if app.config['REMOTE_DEBUGGING']:
    import ptvsd
    ptvsd.enable_attach(
        address=('0.0.0.0', app.config['REMOTE_DEBUGGING_PORT']), redirect_output=True)
    ptvsd.wait_for_attach()
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
