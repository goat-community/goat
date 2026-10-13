"""Idempotent Garage setup for GOAT: layout, access key, buckets, CORS.

Talks to the Garage admin API (v2) and, for CORS, to the S3 API. The compose
bundle and the Helm chart run it from GOAT's image on every start:
``python -m goatlib.storage.garage_init``. It imports the access key pair it
is given (S3_ACCESS_KEY_ID / S3_SECRET_ACCESS_KEY) rather than creating one,
so the services and Garage share the key from one place.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

import boto3
from botocore.config import Config

# Garage's layout capacity is a weight between nodes, not a size limit.
DEFAULT_CAPACITY = 10 * 1024**4

Api = Callable[[str, str, object | None], Any]


@dataclass(frozen=True)
class Settings:
    admin_url: str
    admin_token: str
    s3_url: str
    key_id: str
    key_secret: str
    uploads_bucket: str
    assets_bucket: str
    # Browser origins the uploads bucket's CORS rule allows.
    cors_origins: list[str]
    capacity: int

    @classmethod
    def from_env(cls) -> "Settings":
        public_url = os.environ["GOAT_PUBLIC_URL"].rstrip("/")
        # Defaults to the public URL; a dev machine with several app ports
        # sets more, comma-separated.
        origins = os.environ.get("GARAGE_CORS_ORIGINS") or public_url
        return cls(
            admin_url=os.environ["GARAGE_ADMIN_URL"].rstrip("/"),
            admin_token=os.environ["GARAGE_ADMIN_TOKEN"],
            s3_url=os.environ["GARAGE_S3_URL"],
            key_id=os.environ["S3_ACCESS_KEY_ID"],
            key_secret=os.environ["S3_SECRET_ACCESS_KEY"],
            uploads_bucket=os.environ.get("UPLOADS_BUCKET", "goat-uploads"),
            assets_bucket=os.environ.get("ASSETS_BUCKET", "goat-assets"),
            cors_origins=[
                o.strip().rstrip("/") for o in origins.split(",") if o.strip()
            ],
            capacity=int(
                os.environ.get("GARAGE_CAPACITY_BYTES", str(DEFAULT_CAPACITY))
            ),
        )


def admin_api(settings: Settings) -> Api:
    """A caller of the Garage admin API v2 that raises on HTTP errors."""

    def api(method: str, path: str, body: object | None = None) -> Any:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            f"{settings.admin_url}/v2/{path}",
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {settings.admin_token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as err:
            raise RuntimeError(
                f"{method} {path}: {err.code} {err.read().decode()}"
            ) from err
        return json.loads(raw) if raw else None

    return api


def wait_ready(api: Api, attempts: int = 60, delay: float = 2.0) -> None:
    for _ in range(attempts):
        try:
            api("GET", "GetClusterStatus", None)
            return
        except (OSError, RuntimeError) as err:
            print(f"waiting for garage: {err}")
            time.sleep(delay)
    sys.exit("garage admin API not reachable")


def ensure_layout(api: Api, capacity: int) -> None:
    status = api("GET", "GetClusterStatus", None)
    node = status["nodes"][0]
    if node.get("role"):
        print("layout: already assigned")
        return
    layout = api("GET", "GetClusterLayout", None)
    api(
        "POST",
        "UpdateClusterLayout",
        {
            "roles": [
                {"id": node["id"], "zone": "dc1", "capacity": capacity, "tags": []}
            ]
        },
    )
    api("POST", "ApplyClusterLayout", {"version": layout["version"] + 1})
    print("layout: assigned and applied")


def ensure_key(api: Api, key_id: str, key_secret: str) -> None:
    keys = api("GET", "ListKeys", None)
    if any(k["id"] == key_id for k in keys):
        print("key: present")
        return
    api(
        "POST",
        "ImportKey",
        {"accessKeyId": key_id, "secretAccessKey": key_secret, "name": "goat"},
    )
    print("key: imported")


def ensure_bucket(api: Api, alias: str, key_id: str, website: bool) -> None:
    buckets = api("GET", "ListBuckets", None)
    match = [b for b in buckets if alias in b.get("globalAliases", [])]
    if match:
        bucket_id = match[0]["id"]
    else:
        bucket_id = api("POST", "CreateBucket", {"globalAlias": alias})["id"]
        print(f"bucket {alias}: created")
    api(
        "POST",
        "AllowBucketKey",
        {
            "bucketId": bucket_id,
            "accessKeyId": key_id,
            "permissions": {"read": True, "write": True, "owner": True},
        },
    )
    if website:
        api(
            "POST",
            f"UpdateBucket?id={bucket_id}",
            {
                "websiteAccess": {
                    "enabled": True,
                    "indexDocument": "index.html",
                    "errorDocument": None,
                }
            },
        )
    print(f"bucket {alias}: ready (website={website})")


def ensure_cors(settings: Settings) -> None:
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.s3_url,
        aws_access_key_id=settings.key_id,
        aws_secret_access_key=settings.key_secret,
        region_name="garage",
        config=Config(
            s3={"addressing_style": "path"},
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
        ),
    )
    # Uploads from the GOAT site itself are same-origin and need no CORS; the
    # rule covers other origins such as embeds. Garage compares header names
    # case-sensitively and browsers send them lowercase.
    s3.put_bucket_cors(
        Bucket=settings.uploads_bucket,
        CORSConfiguration={
            "CORSRules": [
                {
                    "AllowedOrigins": settings.cors_origins,
                    "AllowedMethods": ["GET", "HEAD", "PUT"],
                    "AllowedHeaders": ["*"],
                    "ExposeHeaders": ["etag"],
                    "MaxAgeSeconds": 3600,
                }
            ]
        },
    )
    print("cors: set")


def main() -> None:
    settings = Settings.from_env()
    api = admin_api(settings)
    wait_ready(api)
    ensure_layout(api, settings.capacity)
    ensure_key(api, settings.key_id, settings.key_secret)
    ensure_bucket(api, settings.uploads_bucket, settings.key_id, website=False)
    ensure_bucket(api, settings.assets_bucket, settings.key_id, website=True)
    ensure_cors(settings)
    print("garage-init: done")


if __name__ == "__main__":
    main()
