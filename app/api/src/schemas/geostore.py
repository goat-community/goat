from src.db.models import Geostore
from pydantic import validator
import requests

request_examples = {
    "geostore": {
        "configuration": {
            "url": "mapURL",
            "name": "Name",
            "description": "LayerDescription",
            "type": "geoadmin",
            "legend": "legendUrl",
            "attribution": "attribution",
            "getcapabilities": "GetCapabilities",
        },
        "name": "FreiGIS",
        "type": "geoadmin",
        "url": "https://geoportal.freiburg.de/freigis/ressources/services-internet.json",
        "attribution": "Stadt Freiburg im Breisgau",
        "thumbnail_url": "https://s3.eu-central-1.amazonaws.com/goat-app-assets/geostore_thumbnails/freigis.png",
    }
}


class CreateGeostore(Geostore):
    @validator("url", "thumbnail_url")
    def url_returns_200(cls, field_value, values, field, config):
        try:
            result = requests.get(field_value)
            assert result.status_code == 200
        except:
            raise ValueError(f"Could not resolve url from '{field.name}' field.")
        return field_value

    @validator("configuration")
    def validate_configuration_keys(cls, field_value):
        config_keys = request_examples["geostore"]["configuration"].keys()
        if field_value:
            if set(field_value.keys()) != set(config_keys):
                raise ValueError(
                    f'configuration keys should be exactly as of "{", ".join(list(config_keys))}".'
                )
        return field_value

    class Config:
        schema_extra = {"example": request_examples["geostore"]}
