from sqlmodel import SQLModel

class ComputePoiUser(SQLModel):
    data_upload_id : int


"""
Body of the request
"""
request_examples = {
    "compute_poi_user": {"data_upload_id": 1},
    "heatmap_configuration": """{"supermarket":{"sensitivity":250000,"weight":1}}"""
}
