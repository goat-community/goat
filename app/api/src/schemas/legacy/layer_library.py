from src.db import models
from pydantic import root_validator
from .utils import findkeys
from fastapi import HTTPException
from src.legacy.utils.utils import random_lower_string
from datetime import datetime


class RequestExamples:
    @property
    def single_layer_library(self):
        return {
            "url": "https://{a-c}.basemaps.somecdn.com/dark_all/{z}/{x}/{y}.png",
            "legend_urls": [random_lower_string()],
            "special_attribute": {"imagery_set": "Aerial"},
            "access_token": "some_token",
            "map_attribution": "Attribution to the source",
            "date": str(datetime.today().year),
            "source": None,
            "date_1": str(datetime.today().year),
            "source_1": None,
            "style_library_name": None,
            "max_resolution": "0",
            "min_resolution": "0",
            "doc_url": "https://www.plan4better.de",
            "name": random_lower_string(),
            "type": "BING",
        }

    @property
    def single_style_library(self):
        return {
            "translation": {
                "red": {"de": "stressig", "en": "stressful"},
                "grey": {"de": "Lücke im Radnetz", "en": "gap in the cycling network"},
                "black": {"de": "sehr stressig", "en": "very stressful"},
                "green": {"de": "komfortabel", "en": "comfortable"},
                "yellow": {"de": "durchschnittlich", "en": "average"},
            },
            "name": random_lower_string(),
            "style": {
                "name": "munichways",
                "rules": [
                    {
                        "name": "green",
                        "filter": ["==", "farbe", "grün"],
                        "symbolizers": [
                            {
                                "cap": "square",
                                "join": "bevel",
                                "kind": "Line",
                                "color": "#609e72",
                                "width": 2,
                            }
                        ],
                    },
                    {
                        "name": "yellow",
                        "filter": ["==", "farbe", "gelb"],
                        "symbolizers": [
                            {
                                "cap": "square",
                                "join": "bevel",
                                "kind": "Line",
                                "color": "#edc937",
                                "width": 2,
                            }
                        ],
                    },
                    {
                        "name": "red",
                        "filter": ["==", "farbe", "rot"],
                        "symbolizers": [
                            {
                                "cap": "square",
                                "join": "bevel",
                                "kind": "Line",
                                "color": "#df6235",
                                "width": 2,
                            }
                        ],
                    },
                    {
                        "name": "black",
                        "filter": ["==", "farbe", "schwarz"],
                        "symbolizers": [
                            {
                                "cap": "square",
                                "join": "bevel",
                                "kind": "Line",
                                "color": "#000000",
                                "width": 2,
                            }
                        ],
                    },
                    {
                        "name": "grey",
                        "filter": ["==", "farbe", "grau"],
                        "symbolizers": [
                            {
                                "cap": "square",
                                "join": "bevel",
                                "kind": "Line",
                                "color": "#717070",
                                "width": 2,
                            }
                        ],
                    },
                ],
            },
        }


request_examples = RequestExamples()


class CreateLayerLibrary(models.LayerLibrary):
    @root_validator
    def urls_emptiness_vs_type(cls, values):
        # according to the issue: https://github.com/goat-community/goat/issues/1328
        url, the_type = values.get("url"), values.get("type")
        url_mandatory_types = ("WMS", "OSM", "BING")
        if the_type in url_mandatory_types and not url:
            raise ValueError("url should not be empty for the layer type %s." % the_type)

        return values

    @root_validator
    def legend_urls_emptiness_vs_type(cls, values):
        # according to the issue: https://github.com/goat-community/goat/issues/1328
        legend_urls, the_type = values.get("legend_urls"), values.get("type")
        legend_url_mandatory_types = ("WMS",)
        if the_type in legend_url_mandatory_types and not legend_urls:
            raise ValueError("legend_urls should not be empty for the layer type %s." % the_type)

        return values

    @root_validator
    def style_library_name_emptiness_vs_type(cls, values):
        # according to the issue: https://github.com/goat-community/goat/issues/1328
        style_library_name, the_type = values.get("style_library_name"), values.get("type")
        legend_url_mandatory_types = ("MVT", "GEOBUF", "WFS")
        if the_type in legend_url_mandatory_types and not style_library_name:
            raise ValueError(
                "style_library_name should not be empty for the layer type %s." % the_type
            )

        return values

    class Config:
        schema_extra = {"example": request_examples.single_layer_library}


class CreateStyleLibrary(models.StyleLibrary):
    @root_validator
    def translations_present_for_all_names(cls, values):
        style, translation = values.get("style"), values.get("translation")
        rules = style.get("rules")
        translation_keywords_set = set(findkeys(rules, "name"))
        translation_set = set(translation.keys())
        warnings = {}
        # Check if all keywords are present in translation
        if translation_keywords_set != translation_set:
            absent_translations = translation_keywords_set - translation_set
            if absent_translations:
                warnings["absent_translations"] = list(absent_translations)

            # We can find unneeded translations:
            # unneeded_translations = translation_set - translation_keywords_set
            # if unneeded_translations:
            #     warnings["unneeded_translations"] = list(unneeded_translations)

        # Check if all keywords have all translations
        all_languages = set()
        for key in translation.keys():
            # Collect all languages
            all_languages = all_languages.union(set(translation[key].keys()))

        # Search for incomplete translations
        incomplete_translations = []
        for key in translation.keys():
            # Is this keyword have translations for all detected languages?
            if all_languages - set(translation[key].keys()):
                incomplete_translations.append(key)

        if incomplete_translations:
            warnings["incomplete_translations"] = incomplete_translations

        if warnings:
            raise HTTPException(status_code=400, detail=warnings)

        return values

    class Config:
        schema_extra = {"example": request_examples.single_style_library}
