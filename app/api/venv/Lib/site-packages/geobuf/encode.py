# -*- coding: utf-8 -*-

import collections
import json
import sys

import six

from . import geobuf_pb2


class Encoder:

    geometry_types = {
        'Point': 0,
        'MultiPoint': 1,
        'LineString': 2,
        'MultiLineString': 3,
        'Polygon': 4,
        'MultiPolygon': 5,
        'GeometryCollection': 6
    }

    def encode(self, data_json, precision=6, dim=2):
        obj = self.json = data_json
        data = self.data = geobuf_pb2.Data()

        self.precision = precision
        self.dim = dim
        self.e = pow(10, precision) # multiplier for converting coordinates into integers

        self.keys = collections.OrderedDict()
        self.transformed = False
        self.is_topo = False

        data_type = obj['type']

        if data_type == 'FeatureCollection': self.encode_feature_collection(data.feature_collection, obj)
        elif data_type == 'Feature': self.encode_feature(data.feature, obj)
        elif data_type == 'Topology': self.encode_topology(data.topology, obj)
        else: self.encode_geometry(data.geometry, obj)

        # print tf.MessageToString(data)

        return data.SerializeToString()


    def encode_feature_collection(self, feature_collection, feature_collection_json):
        self.encode_custom_properties(feature_collection, feature_collection_json, ('type', 'features'))
        for feature_json in feature_collection_json.get('features'):
            self.encode_feature(feature_collection.features.add(), feature_json)


    def encode_feature(self, feature, feature_json):
        self.encode_id(feature, feature_json.get('id'))
        self.encode_properties(feature, feature_json.get('properties'))
        self.encode_custom_properties(feature, feature_json, ('type', 'id', 'properties', 'geometry'))
        self.encode_geometry(feature.geometry, feature_json.get('geometry'))


    def encode_topology(self, topology, data_json):

        self.is_topo = True

        transform_json = data_json.get('transform')

        if transform_json:
            scale_json = transform_json.get('scale')
            translate_json = transform_json.get('translate')

            transform = topology.transform
            transform.scale_x = scale_json[0]
            transform.scale_y = scale_json[1]
            transform.translate_x = translate_json[0]
            transform.translate_y = translate_json[1]

            self.transformed = True

        self.encode_custom_properties(topology, data_json, ('type', 'transform', 'arcs', 'objects'))

        arcs = data_json.get('arcs')
        for arc in arcs: topology.lengths.append(len(arc))
        for arc in arcs:
            for p in arc: self.add_point(topology.coords, p)

        for name, geom in data_json.get('objects').items():
            topology.names.append(name);
            self.encode_geometry(topology.objects.add(), geom)


    def encode_geometry(self, geometry, geometry_json):

        gt = geometry_json['type']
        coords = geometry_json.get('coordinates')
        coords_or_arcs = coords

        geometry.type = self.geometry_types[gt]

        self.encode_custom_properties(geometry, geometry_json,
            ('type', 'id', 'coordinates', 'arcs', 'geometries', 'properties'))

        if self.is_topo:
            coords_or_arcs = geometry_json.get('arcs')
            self.encode_id(geometry, geometry_json.get('id'))
            self.encode_properties(geometry, geometry_json.get('properties'))

        if gt == 'GeometryCollection':
            for geom in geometry_json.get('geometries'): self.encode_geometry(geometry.geometries.add(), geom)

        elif gt == 'Point':
            self.add_point(geometry.coords, coords)

        elif gt == 'MultiPoint':
            self.add_line(geometry.coords, coords, True)

        elif gt == 'LineString':
            self.add_line(geometry.coords, coords_or_arcs)

        elif gt == 'MultiLineString' or gt == 'Polygon':
            self.add_multi_line(geometry, coords_or_arcs)

        elif gt == 'MultiPolygon':
            self.add_multi_polygon(geometry, coords_or_arcs)


    def encode_properties(self, obj, props_json):
        if props_json is None: return

        for key, val in props_json.items():
            self.encode_property(key, val, obj.properties, obj.values)


    def encode_custom_properties(self, obj, obj_json, exclude):
        for key, val in obj_json.items():
            if not (key in exclude):
                self.encode_property(key, val, obj.custom_properties, obj.values)


    def encode_property(self, key, val, properties, values):
        keys = self.keys

        if not (key in keys):
            keys[key] = True
            self.data.keys.append(key)
            keyIndex = len(self.data.keys) - 1
        else:
            keyIndex = list(keys.keys()).index(key)

        value = values.add()

        if isinstance(val, dict) or isinstance(val, list):
            value.json_value = json.dumps(val, separators=(',',':'))

        elif isinstance(val, six.text_type): value.string_value = val
        elif isinstance(val, float):
            if val.is_integer(): self.encode_int(int(val), value)
            else: value.double_value = val
        elif isinstance(val, bool): value.bool_value = val
        elif isinstance(val, six.integer_types): self.encode_int(val, value)


        properties.append(keyIndex)
        properties.append(len(values) - 1)


    def encode_int(self, val, value):
        try:
            if val >= 0: value.pos_int_value = val;
            else: value.neg_int_value = -val;
        except ValueError:
            value.double_value = val


    def encode_id(self, obj, id):
        if id is not None:
            if isinstance(id, int): obj.int_id = id
            else: obj.id = str(id)


    def add_coord(self, coords, coord):
        coords.append(coord if self.transformed else int(round(coord * self.e)))

    def add_point(self, coords, point):
        for x in point: self.add_coord(coords, x)

    def add_line(self, coords, points, is_multi_point=False):
        r = range(self.dim)
        for i, p in enumerate(points):
            if self.is_topo and not is_multi_point: # delta-encode arc indexes
                coords.append(p - (points[i - 1] if i else 0))
            else: # delta-encode coordinates
                for j in r: self.add_coord(coords, p[j] - (points[i - 1][j] if i else 0))


    def add_multi_line(self, geometry, lines):
        if len(lines) != 1:
            for points in lines: geometry.lengths.append(len(points))

        for points in lines: self.add_line(geometry.coords, points)


    def add_multi_polygon(self, geometry, polygons):
        if len(polygons) != 1 or len(polygons[0]) != 1:
            geometry.lengths.append(len(polygons))
            for rings in polygons:
                geometry.lengths.append(len(rings))
                for points in rings: geometry.lengths.append(len(points))

        for rings in polygons:
            for points in rings: self.add_line(geometry.coords, points)
