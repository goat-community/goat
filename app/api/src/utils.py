import json
import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import emails
import geobuf
import numpy as np
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
            "de": "Passwort zurücksetzen",
        },
        "template_name": "reset_password",
    },
    "activate_new_account": {
        "url": f"{settings.SERVER_HOST}/activate-account?token=",
        "subject": {
            "en": "Activate your account",
            "de": "Demo aktivieren",
        },
        "template_name": "activate_new_account",
    },
    "account_trial_started": {
        "url": "",
        "subject": {
            "en": "Your GOAT demo is ready to use",
            "de": "Ihre GOAT Demo steht bereit",
        },
        "template_name": "account_trial_started",
    },
    "account_expired": {
        "url": "",
        "subject": {"en": "Account expired", "de": "Demo abgelaufen"},
        "template_name": "account_expired",
    },
    "account_expiring": {
        "url": "",
        "subject": {"en": "Account expiring soon", "de": "Demo bald ablaufen"},
        "template_name": "account_expiring",
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


def decode_r5_grid(grid_data_buffer: bytes) -> Any:
    """
    Decode R5 grid data
    """
    CURRENT_VERSION = 0
    HEADER_ENTRIES = 7
    HEADER_LENGTH = 9  # type + entries
    TIMES_GRID_TYPE = "ACCESSGR"

    # -- PARSE HEADER
    ## - get header type
    header = {}
    header_data = np.frombuffer(grid_data_buffer, count=8, dtype=np.byte)
    header_type = "".join(map(chr, header_data))
    if header_type != TIMES_GRID_TYPE:
        raise ValueError("Invalid grid type")
    ## - get header data
    header_raw = np.frombuffer(grid_data_buffer, count=HEADER_ENTRIES, offset=8, dtype=np.int32)
    version = header_raw[0]
    if version != CURRENT_VERSION:
        raise ValueError("Invalid grid version")
    header["zoom"] = header_raw[1]
    header["west"] = header_raw[2]
    header["north"] = header_raw[3]
    header["width"] = header_raw[4]
    header["height"] = header_raw[5]
    header["depth"] = header_raw[6]
    header["version"] = version

    # -- PARSE DATA --
    gridSize = header["width"] * header["height"]
    # - skip the header
    data = np.frombuffer(
        grid_data_buffer,
        offset=HEADER_LENGTH * 4,
        count=gridSize * header["depth"],
        dtype=np.int32,
    )
    # - reshape the data
    data = data.reshape(header["depth"], gridSize)
    reshaped_data = np.array([])
    for i in range(header["depth"]):
        reshaped_data = np.append(reshaped_data, data[i].cumsum())
    data = reshaped_data
    # - decode metadata
    raw_metadata = np.frombuffer(
        grid_data_buffer,
        offset=(HEADER_LENGTH + header["width"] * header["height"] * header["depth"]) * 4,
        dtype=np.int8,
    )
    metadata = json.loads(raw_metadata.tostring())
    def contains(x, y, z):
        return (
            x >= 0
            and x < header["width"]
            and y >= 0
            and y < header["height"]
            and z >= 0
            and z < header["depth"]
        )
    def get(x, y, z):
        if contains(x, y, z):
            return data[z * gridSize + y * header["width"] + x]
        else:
            return None

    return (
        header
        | metadata
        | {"data": data, "errors": [], "warnings": [], "contains": contains, "get": get}
    )


def encode_r5_grid(grid_data: Any) -> bytes:
    """
    Encode raster grid data
    """
    return geobuf.encode(grid_data)


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
    print(f"[bold green]INFO[/bold green]: {message}")


def print_warning(message: str):
    print(f"[bold red]WARNING[/bold red]: {message}")
