import json


class GeoJSON(dict):

    def __str__(self):
        return json.dumps(self)
