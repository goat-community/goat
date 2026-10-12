"""Idempotent Garage setup for GOAT: layout, access key, buckets, CORS.

Talks to the Garage admin API (v2) and, for CORS, to the S3 API.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

import boto3
from botocore.config import Config

ADMIN = os.environ["GARAGE_ADMIN_URL"].rstrip("/")
TOKEN = os.environ["GARAGE_ADMIN_TOKEN"]
KEY_ID = os.environ["S3_ACCESS_KEY_ID"]
KEY_SECRET = os.environ["S3_SECRET_ACCESS_KEY"]
PUBLIC_URL = os.environ["GOAT_PUBLIC_URL"].rstrip("/")
# Browser origins allowed by the uploads bucket's CORS rule, comma-separated.
# Defaults to the public URL; a dev machine with several app ports sets more.
CORS_ORIGINS = [
    o.strip().rstrip("/")
    for o in (os.environ.get("GARAGE_CORS_ORIGINS") or PUBLIC_URL).split(",")
    if o.strip()
]
UPLOADS = os.environ.get("UPLOADS_BUCKET", "goat-uploads")
ASSETS = os.environ.get("ASSETS_BUCKET", "goat-assets")
CAPACITY = int(os.environ.get("GARAGE_CAPACITY_BYTES", str(10 * 1024**4)))


def api(method: str, path: str, body: object | None = None) -> object:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{ADMIN}/v2/{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
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


def wait_ready() -> None:
    for _ in range(60):
        try:
            api("GET", "GetClusterStatus")
            return
        except (OSError, RuntimeError) as err:
            print(f"waiting for garage: {err}")
            time.sleep(2)
    sys.exit("garage admin API not reachable")


def ensure_layout() -> None:
    status = api("GET", "GetClusterStatus")
    node = status["nodes"][0]
    if node.get("role"):
        print("layout: already assigned")
        return
    layout = api("GET", "GetClusterLayout")
    api(
        "POST",
        "UpdateClusterLayout",
        {
            "roles": [
                {"id": node["id"], "zone": "dc1", "capacity": CAPACITY, "tags": []}
            ]
        },
    )
    api("POST", "ApplyClusterLayout", {"version": layout["version"] + 1})
    print("layout: assigned and applied")


def ensure_key() -> None:
    keys = api("GET", "ListKeys")
    if any(k["id"] == KEY_ID for k in keys):
        print("key: present")
        return
    api(
        "POST",
        "ImportKey",
        {"accessKeyId": KEY_ID, "secretAccessKey": KEY_SECRET, "name": "goat"},
    )
    print("key: imported")


def ensure_bucket(alias: str, website: bool) -> None:
    buckets = api("GET", "ListBuckets")
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
            "accessKeyId": KEY_ID,
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


def ensure_cors() -> None:
    s3 = boto3.client(
        "s3",
        endpoint_url=os.environ["GARAGE_S3_URL"],
        aws_access_key_id=KEY_ID,
        aws_secret_access_key=KEY_SECRET,
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
        Bucket=UPLOADS,
        CORSConfiguration={
            "CORSRules": [
                {
                    "AllowedOrigins": CORS_ORIGINS,
                    "AllowedMethods": ["GET", "HEAD", "PUT"],
                    "AllowedHeaders": ["*"],
                    "ExposeHeaders": ["etag"],
                    "MaxAgeSeconds": 3600,
                }
            ]
        },
    )
    print("cors: set")


if __name__ == "__main__":
    wait_ready()
    ensure_layout()
    ensure_key()
    ensure_bucket(UPLOADS, website=False)
    ensure_bucket(ASSETS, website=True)
    ensure_cors()
    print("garage-init: done")
