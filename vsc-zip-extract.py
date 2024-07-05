import argparse
import hashlib
import http.client
import json
import re

from pathlib import Path
from tqdm import tqdm

HASH_API_HOSTNAME = "update.code.visualstudio.com"
PROXY_HOSTNAME = "proxy01.intra.hkma.gov.hk"
PROXY_PORT = 8080


def backup_old_path() -> None:
    pass

def _extract_version_str(filename_stem: str) -> str:
    """Extract the version number string, assuming semantic versioning, i.e. X.Y.Z where
        X: Major, Y: Minor, Z: Patch

    Args:
        filename_stem (str): A str containing the stem of the filename

    Returns:
        str: Version number string X.Y.Z
    """
    pattern = r"(\d+\.\d+\.\d+)"
    match = re.search(pattern, filename_stem)

    if match:
        version = match.group(1)
    else:
        version = ""

    return version

def _build_hash_url_path(version: str, platform_os: str = "win32-x64-archive", build: str = "stable") -> str:
    """Returns the VSCode hash value URL path (without the hostname), e.g.
        "/api/versions/1.91.0/win32-x64-archive/stable/"

    Args:
        version (str): Version number string X.Y.Z

    Returns:
        str: The URL path without the hostname
    """

    return f"/api/versions/{version}/{platform_os}/{build}/"

def _get_file_hash(filename: Path) -> str:
    """Generate a hash value for the file in the path `filename`

    Args:
        filename (Path): File to be generated a hash value

    Returns:
        str: The SHA-256 hash value of the file
    """

    with open(filename, "rb") as f:
        digest = hashlib.file_digest(f, "sha256")

    return digest.hexdigest()

def _get_online_hash(url_hostname: str, url_path: str) -> str:
    """Get the hash value published by the online API

    Args:
        url_hostname (str): The hostname of the API
        url_path (str): The request path of the API

    Raises:
        http.client.ResponseNotReady: When the HTTP request status is not OK

    Returns:
        str: The hash value returned by the API
    """
    conn = http.client.HTTPSConnection(PROXY_HOSTNAME, PROXY_PORT)
    conn.set_tunnel(url_hostname)
    conn.request("GET", url_path)
    response = conn.getresponse()

    if response.status == http.client.OK:
        response_data = response.read()
    else:
        raise http.client.ResponseNotReady
    conn.close()

    response_json = json.loads(response_data.decode())

    return response_json["hash"]


def verify_download(filename: Path) -> bool:
    """Verifty the downloaded file by comparing its hash value against online

    Args:
        filename (Path): File to be verified

    Returns:
        bool: True if the file is verified, False otherwise
    """

    version = _extract_version_str(filename.stem)
    url_path = _build_hash_url_path(version)
    expected_hash_value = _get_online_hash(HASH_API_HOSTNAME, url_path)

    actual_hash_value = _get_file_hash(filename)

    if actual_hash_value == expected_hash_value:
        verified = True
    else:
        verified = False

    return verified

def extract_zip(filename: Path) -> None:
    pass

def migrate_user_data() -> None:
    pass

def remove_old_path(install_path: Path | None) -> None:
    pass

def main() -> None:
    pass

if __name__ == "__main__":
    main()
