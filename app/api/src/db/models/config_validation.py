from schema import And, Optional, Schema, SchemaError, Use

# Function to check if dict schema is valid
def check_dict_schema(conf_schema, conf):
    try:
        conf_schema.validate(conf)
        return True
    except SchemaError:
        return False

#Schemas for POIs and Layers
PoiCategory = Schema(
    {
        str: {
            "icon": str,
            "color": [str],
            Optional("multiple_entrance"): bool,
        }
    }
)

PoiGroup = Schema(
    {
        str: 
        {
            "icon": str, 
            "color": [str], 
            "children": [PoiCategory]
        }
    }
)

PoiCategoryUpdate = Schema(
  {
      str: PoiCategory
  }
)

LayerCategory = Schema(
    {
        str: {
            "url": str,
            "type": And(lambda n : n in ['OSM', 'BING', 'MVT', 'XYZ', 'GEOJSON', 'WMS', 'WFS', 'GEOBUF'], str),
            Optional("map_attribution"): bool,
            Optional("imagery_set"): str,
            Optional("access_token"): str,
            Optional("attributes"): dict,
            Optional("style"): dict, 
        }
    }
)

LayerCategory = Schema(
    {
        str: 
        {
            "icon": str, 
            "children": [LayerCategory]
        }
    }
)

LayerCategoryUpdate = Schema(
  {
    str: LayerCategory
  }
)