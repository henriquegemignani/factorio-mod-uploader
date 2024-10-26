# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
# ]
# ///

import argparse
import json
import re
import sys
import zipfile
from os import getenv
from pathlib import Path

import requests

parser = argparse.ArgumentParser()
parser.add_argument("zip_file", type=Path, help="Path to the zip file to upload")
args = parser.parse_args()

MOD_PORTAL_URL = "https://mods.factorio.com"
INIT_UPLOAD_URL = f"{MOD_PORTAL_URL}/api/v2/mods/releases/init_upload"

apikey = getenv("MOD_UPLOAD_API_KEY")
zipfile_path: Path = args.zip_file

with zipfile.ZipFile(zipfile_path) as z:
    info_path = [name for name in z.namelist() if re.match(r"[^/]+/info.json", name)]
    if len(info_path) != 1:
        print(f"Expected to find a single info.json, but found {info_path}")
        sys.exit(1)

    info = json.loads(z.open(info_path[0]).read().decode())
    mod_name = info["name"]

request_body = data = {"mod": mod_name}
request_headers = {"Authorization": f"Bearer {apikey}"}

response = requests.post(INIT_UPLOAD_URL, data=request_body, headers=request_headers)

if not response.ok:
    print(f"init_upload failed: {response.text}")
    sys.exit(1)

upload_url = response.json()["upload_url"]

with zipfile_path.open("rb") as f:
    request_body = {"file": f}
    response = requests.post(upload_url, files=request_body)

if not response.ok:
    print(f"upload failed: {response.text}")
    sys.exit(1)

print(f"upload successful: {response.text}")
