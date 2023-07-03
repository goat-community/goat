
"""
Body of the request
"""
request_examples = {
    "create": {
        "map": {"zoom": 13, "max_zoom": 21, "min_zoom": 10, "projection_code": "EPSG:3857"}
    },
    "user_customization_insert": {
        "poi": {
            "summary": "Update POI setting",
            "value": {"nursery": {"icon": "fa-solid fa-dumbbell", "color": ["#ff0000"]}},
        }
    },
    "user_customization_delete": {"poi": {"summary": "Delete POI setting", "value": "nursery"}},
}
