from src.schemas.heatmap import ReturnTypeHeatmap
from src.schemas.isochrone import IsochroneOutputType


def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x


def validate_return_type(results, return_type=None):
    if return_type is None:
        return_type = results["return_type"]

    allowed_return_types = {
        "heatmap": {member.value for member in ReturnTypeHeatmap},
        "isochrone": {member.value for member in IsochroneOutputType},
    }
    data_source = results["data_source"]
    if data_source not in allowed_return_types.keys():
        data_source = "heatmap"
    if return_type not in allowed_return_types[data_source]:
        raise ValueError(
            f"Invalid return type '{return_type}' for data source '{results['data_source']}'. "
        )
