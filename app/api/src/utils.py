import json
import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import emails
import geobuf
from emails.template import JinjaTemplate
from fastapi import HTTPException
from geoalchemy2.shape import to_shape
from geojson import Feature, FeatureCollection
from geojson import loads as geojsonloads
from jose import jwt
from rich import print as print
from starlette.responses import Response

from src.core.config import settings
from src.resources.enums import MimeTypes


def send_email_(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST.upper(), "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"send email result: {response}")


def send_test_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME.upper()
    subject = f"{project_name} - Test email"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template_str = f.read()
    send_email_(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME.upper(), "email": email_to},
    )


email_content_config = {
    "password_recovery": {
        "url": f"{settings.SERVER_HOST}/reset-password?token=",
        "subject": {
            "en": "Password recovery",
            "de": "Passwort-Wiederherstellung",
        },
        "template_name": "reset_password",
    },
    "activate_new_account": {
        "url": f"{settings.SERVER_HOST}/activate-account?token=",
        "subject": {
            "en": "Activate your account",
            "de": "Aktiviere dein Konto",
        },
        "template_name": "activate_new_account",
    },
}


def send_email(
    type: str,
    email_to: str,
    name: str,
    surname: str,
    token: str = "",
    email_language: str = "en",
) -> None:
    if type not in email_content_config:
        raise ValueError(f"Unknown email type {type}")

    subject = email_content_config[type]["subject"][email_language]
    template_str = ""
    available_email_language = "en"
    template_file_name = email_content_config[type]["template_name"]
    link = email_content_config[type]["url"] + token
    if os.path.isfile(
        Path(settings.EMAIL_TEMPLATES_DIR) / f"{template_file_name}_{email_language}.html"
    ):
        available_email_language = email_language
    try:
        with open(
            Path(settings.EMAIL_TEMPLATES_DIR)
            / f"{template_file_name}_{available_email_language}.html"
        ) as f:
            template_str = f.read()
    except OSError:
        print(f"No template for language {available_email_language}")

    send_email_(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME.upper(),
            "name": name,
            "surname": surname,
            "email": email_to,
            "valid_hours": settings.EMAIL_TOKEN_EXPIRE_HOURS,
            "url": link,
        },
    )


def generate_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.API_SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.API_SECRET_KEY, algorithms=["HS256"])
        return decoded_token["sub"]
    except jwt.JWTError:
        return None


def return_geojson_or_geobuf(
    features: Any,
    return_type: str = "geojson",
) -> Any:
    """
    Return geojson or geobuf
    """

    if return_type == "geojson":
        return json.loads(json.dumps(features))
    elif return_type == "geobuf":
        return Response(bytes(geobuf.encode(features)), media_type=MimeTypes.geobuf.value)
    elif return_type == "db_geobuf":
        return Response(bytes(features))
    else:
        raise HTTPException(status_code=400, detail="Invalid return type")


def to_feature_collection(
    sql_result: Any,
    geometry_name: str = "geom",
    geometry_type: str = "wkb",  # wkb | geojson (wkb is postgis geometry which is stored as hex)
    exclude_properties: List = [],
) -> FeatureCollection:
    """
    Generic method to convert sql result to geojson. Geometry field is expected to be in geojson or postgis hex format.
    """
    if not isinstance(sql_result, list):
        sql_result = [sql_result]

    exclude_properties.append(geometry_name)
    features = []
    for row in sql_result:
        if not isinstance(row, dict):
            dict_row = dict(row)
        else:
            dict_row = row
        geometry = None
        if geometry_type == "wkb":
            geometry = to_shape(dict_row[geometry_name])
        elif geometry_type == "geojson":
            geometry = geojsonloads(dict_row[geometry_name])

        features.append(
            Feature(
                id=dict_row.get("gid") or dict_row.get("id") or 0,
                geometry=geometry,
                properties=without_keys(dict_row, exclude_properties),
            )
        )
    return FeatureCollection(features)


def without_keys(d, keys):
    """
    Omit keys from a dict
    """
    return {x: d[x] for x in d if x not in keys}


def delete_file(file_path: str) -> None:
    """Delete file from disk."""
    try:
        os.remove(file_path)
    except OSError as e:
        pass


def delete_dir(dir_path: str) -> None:
    """Delete file from disk."""
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        pass


def clean_unpacked_zip(dir_path: str, zip_path: str) -> None:
    """Delete unpacked zip file and directory."""
    delete_dir(dir_path)
    delete_file(zip_path)


def print_hashtags():
    print(
        "#################################################################################################################"
    )


def print_info(message: str):
    print(f"INFO: {message}")


def print_warning(message: str):
    print(f"WARNING: {message}")
