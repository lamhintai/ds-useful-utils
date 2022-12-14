"""Read a generated conda package url list, as generated by conda list --explicit,
and download the package installation files for offline installation on servers
that are not connected to internet. The OS of the servers can be different from
the input package list.

Usage:
    build_conda_channel.py <path_to_urls.txt> <output_folder_path>

Example:
    build_conda_channel.py C:/Users/<user>/Miniconda3/pkgs C:/offline_conda_channel

Note:
    Run `conda index <output_folder_path>/<platform>` for each <platform>
    (arch in conda terms), e.g. linux-64, osx-64, win-64.
    By default this script only downloads for linux-64.
"""

from itertools import repeat
import logging
import multiprocessing.dummy as mp
import os
import requests
import sys
from tqdm import tqdm

# Full list:
# TARGET_ARCHS = ["linux-64", "osx-64", "win-64"]
TARGET_ARCHS = ["linux-64"]

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def read_pkg_urls(env_pkg_file_path):
    with open(env_pkg_file_path) as f:
        pkg_urls = f.readlines()

    # Align path separators to forward slash
    return [pkg_url.replace("\\", "/").rstrip("\n") for pkg_url in pkg_urls]


def get_arch_pkg(pkg_url):
    url_splits = pkg_url.split("/")
    packages = url_splits[-1]
    archs = url_splits[-2]
    return (archs, packages, pkg_url)


def download_file(pkg_dl_args):
    # Unpack arguments, which are zipped due to calling by imap
    pkg_url, file_destination_path = pkg_dl_args

    logging.debug(f"pkg_url: {pkg_url}")
    logging.debug(f"file_destination_path: {file_destination_path}")

    resp = requests.get(pkg_url)

    try:
        if resp.status_code == 200:
            with open(file_destination_path, "wb") as f:
                f.write(resp.content)
                logging.info(f"File saved: {file_destination_path}")
        else:
            resp.raise_for_status()
    except BaseException as e:
        logging.error(f"Cannot download: {pkg_url}, status: {resp.status_code}")


def download_pkgs(arch_pkg_url_list, output_path):
    logging.info(f"Platform targets: {TARGET_ARCHS}")

    for target_arch in TARGET_ARCHS:
        logging.info(f"Getting packages for {target_arch}...")
        file_destination_path = os.path.join(output_path, target_arch)

        if not os.path.exists(file_destination_path):
            os.makedirs(file_destination_path)

        existing_pkgs = os.listdir(file_destination_path)
        download_url_list = []
        file_destination_path_list = []

        logging.debug(f"existing_pkgs: {existing_pkgs}")
        logging.debug(arch_pkg_url_list)

        for current_arch, package, current_pkg_url in arch_pkg_url_list:
            if package not in existing_pkgs:
                new_url = current_pkg_url.replace(current_arch, target_arch)
                download_url_list.append(new_url)
                file_destination_path_list.append(
                    os.path.join(file_destination_path, package)
                )
        logging.debug(download_url_list)

        n = len(download_url_list)

        with mp.Pool() as pool:
            tqdm(
                pool.map(
                    download_file, zip(download_url_list, file_destination_path_list)
                ),
                total=n,
            )

        logging.info(f"Download complete for {target_arch}.")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {__file__} <path_to_urls.txt> <output_folder_path>")
        exit(1)

    env_pkg_file_path = sys.argv[1]
    output_path = os.path.realpath(sys.argv[2])

    pkg_urls = read_pkg_urls(env_pkg_file_path)
    arch_pkg_url_list = [get_arch_pkg(url) for url in pkg_urls]
    download_pkgs(arch_pkg_url_list, output_path)


if __name__ == "__main__":
    main()
