from src.db.models import Geostore
from pydantic import validator
import requests
from src.legacy.utils.utils import random_lower_string


class RequestExamples:
    @property
    def geostore(self):
        return {
            "configuration": {
                "url": "mapURL",
                "name": "Name",
                "description": "LayerDescription",
                "type": "geoadmin",
                "legend": "legendUrl",
                "attribution": "attribution",
                "getcapabilities": "GetCapabilities",
            },
            "name": "test_" + random_lower_string(),
            "type": "geoadmin",
            "url": "https://geoportal.freiburg.de/freigis/ressources/services-internet.json",
            "attribution": "Stadt Freiburg im Breisgau",
            "thumbnail_url": "https://s3.eu-central-1.amazonaws.com/goat-app-assets/geostore_thumbnails/freigis.png",
        }


request_examples = RequestExamples()


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
        if field_value:
            config_keys = request_examples.geostore["configuration"].keys()
            if not set(config_keys).issuperset(set(field_value.keys())):
                raise ValueError(
                    f'configuration keys should be subset of "{", ".join(list(config_keys))}".'
                )
        return field_value

    @validator("configuration")
    def remove_empty_configuration(cls, field_value):
        if field_value:
            return {k: v for k, v in field_value.items() if v}

    class Config:
        schema_extra = {"example": request_examples.geostore}
