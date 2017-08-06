import json
import hashlib
import logging
import os
import sys
import tempfile
from subprocess import check_output

log = logging.getLogger(__name__)

BASE_URL = "https://pypi.python.org"


def get_hash(url):
    # the file name is at the end after the last slash
    file_name = url.rsplit("/", 1)[-1]
    for fl in files:
        if fl == file_name:
            with open(path + "/" + fl, 'rb') as r_f:
                return hashlib.sha256(r_f.read()).hexdigest()


def construct_json(pkg_name, rel_url):
    url_pkg = BASE_URL + relative_url
    data_json = {'name': pkg_name, 'build-options': {}, 'sources': [{}, {}, {}]}
    data_json['build-options']['env'] = {}
    data_json['build-options']['env']['PYTHONUSERBASE'] = '/app'
    data_json['sources'][0]['type'] = 'archive'
    data_json['sources'][0]['url'] = url_pkg
    file_hash = get_hash(rel_url)
    data_json['sources'][0]['sha256'] = file_hash
    data_json['sources'][1]['type'] = 'script'
    data_json['sources'][1]['dest-filename'] = 'configure'
    data_json['sources'][1]['commands'] = ["echo just so that a configure file exists"]
    data_json['sources'][2]['type'] = "file"
    data_json['sources'][2]['path'] = "pip-Makefile"
    data_json['sources'][2]['dest-filename'] = "Makefile"
    return data_json

if __name__ == "__main__":
    path = tempfile.TemporaryDirectory().name
    print("Downloading and checking the required dependencies.\n"
          "Depending on your Internet connection and CPU this operation may take a while.\n"
          "Please wait.")
    data_log = check_output("pip3 -v --no-cache-dir download " + " ".join(sys.argv[1:]) +
                            " -d " + path + " --no-binary :all:", shell=True)
    data_log = data_log.decode()

    files = os.listdir(path)
    for file in files:
        log.info("Downloaded %s", file)

    packages = []
    packages_ordered = []

    for line in data_log.splitlines():
        if "Collecting" in line:
            # Save only the package name
            package = line.split()[1]
            packages.append(package)
            # Remove the Collecting word
            package_full = line.rsplit(" ", 1)[1]
            packages_ordered.append(package_full)

    json_output = []

    for line in data_log.splitlines():
        if "GET /packages" in line:
            for package in packages:
                # Simply remove any extra information.
                # The packages versions that we have were already
                # checked with pip
                pkg, _, _ = package.partition("!")
                pkg, _, _ = pkg.partition("=")
                pkg, _, _ = pkg.partition(">")
                pkg, _, _ = pkg.partition("<")
                pkg, _, _ = pkg.partition("[")
                if pkg.lower() in line.lower():
                    relative_url = line.split()[1]
                    pkg_json = construct_json(pkg, relative_url)
                    json_output.append(pkg_json)
                    # remove the found package
                    packages.remove(package)
                    break

    # this is not enough because the same package may be a dependency
    # for multiple other packages, and the installing order is important
    json_output.reverse()

    with open("output.json", "w") as output:
        json.dump(json_output, output, indent=4)
