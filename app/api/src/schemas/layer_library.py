from sentry_sdk import HttpTransport
from src.db import models
from pydantic import root_validator
from .utils import findkeys
from fastapi import HTTPException


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
        schema_extra = {
            "example": {
                "url": "https://{a-c}.basemaps.somecdn.com/dark_all/{z}/{x}/{y}.png",
                "legend_urls": None,
                "special_attribute": {"imagery_set": "Aerial"},
                "access_token": "some_token",
                "map_attribution": "Attribution to the source",
                "date": None,
                "source": None,
                "date_1": None,
                "source_1": None,
                "style_library_name": None,
                "max_resolution": None,
                "min_resolution": None,
                "name": "test",
                "type": "BING",
            }
        }


class CreateStyleLibrary(models.StyleLibrary):
    @root_validator
    def translations_present_for_all_names(cls, values):
        style, translation = values.get("style"), values.get("translation")
        rules = style.get("rules")
        translation_keyworkds_set = set(findkeys(rules, "name"))
        translation_set = set(translation.__keys__)
        warnings = {}
        # Check if all keywords are present in translation
        if translation_keyworkds_set != translation_set:
            absent_translations = translation_set - translation_keyworkds_set
            if absent_translations:
                warnings["absent_translations"] = absent_translations

            # We can find unneeded translations:
            # unneeded_translations = translation_keyworkds_set - translation_set
            # if unneeded_translations:
            #     warnings["unneeded_translations"] = unneeded_translations

        # Check if all keywords have all translations
        all_languages = set()
        for key in translation.__keys__:
            # Collect all languages
            all_languages = all_languages.union(set(translation[key].__keys__))

        # Search for incomplete translations
        incomplete_translations = []
        for key in translation.__keys__:

            # Is this keyword have translations for all detected languages?
            if all_languages - set(translation[key].__keys__):
                incomplete_translations.append(key)

        if incomplete_translations:
            warnings["incomplete_translations"] = incomplete_translations

        if warnings:
            raise HTTPException(status_code=400, detail=warnings)
