from pydantic import BaseModel


class CutomDataUploadState(BaseModel):
    data_upload_id: int
    state: bool


request_examples = {"poi_category": "french_bakery", "delete_upload": 1}
