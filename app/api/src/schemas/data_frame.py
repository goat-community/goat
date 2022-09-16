from fastapi import HTTPException


def validate_data_frame(data_frame):
    if not data_frame.crs:
        raise HTTPException(status_code=400, detail="Invalid CRS")
    if data_frame.crs.name == "unknown":
        raise HTTPException(status_code=400, detail="Invalid CRS")
