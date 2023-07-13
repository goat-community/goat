from schema import And, Optional, Schema, SchemaError


# Function to check if dict schema is valid
def check_dict_schema(conf_schema, conf):
    try:
        conf_schema.validate(conf)
        return True
    except SchemaError:
        return False

mapping_setting_type = {"poi": "poi_groups", "layer": "layer_groups"}

# Schemas for POIs and Layers
PoiCategory = Schema(
    {
        str: {
            "icon": str,
            "color": [str],
            Optional("multiple_entrance"): bool,
            Optional("sensitivity"): int,
        }
    }
)

PoiGroup = Schema({str: {"icon": str, "color": [str], "children": [PoiCategory]}})

PoiGroups = Schema({"poi_groups": [PoiGroup]})

OtherPoiGroupDummy =  {"other": {
                            "icon": "fas fa-circle",
                            "color": ["#717171"],
                            "children": {}
                        }}


LayerCategory = Schema(
    {
        str: {
            Optional("url"): str,
            "type": And(
                lambda n: n in ["OSM", "BING", "MVT", "XYZ", "GEOJSON", "WMS", "WFS", "GEOBUF"],
                str,
            ),
            Optional("map_attribution"): str,
            Optional("imagery_set"): str,
            Optional("access_token"): str,
            Optional("attributes"): dict,
            Optional("translation"): dict,
            Optional("style"): dict,
        }
    }
)

LayerGroup = Schema({str: {"icon": str, "children": [LayerCategory]}})

LayerGroups = Schema({"layer_groups": [LayerGroup]})

HeatmapConfiguration = Schema({str: {"sensitivity": int, "weight": int}})
