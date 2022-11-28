#!/usr/bin/env python3

import argparse
from collections import defaultdict
import re

import pymongo
import plotly.express as px


from bson.objectid import ObjectId

from javus.utils import MongoConnection

db_config = {
    "database": "javacard-analysis",
    "host": "localhost",
    "port": "27017",
}

jc_sdks = [
    "jc211",
    "jc310b43",
    "jc221",
    "jc222",
    "jc303",
    "jc304",
    "jc305u1",
    "jc305u2",
    "jc305u3",
]


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "object_id", help="The ID of the object run that is to be visualized"
    )
    args = parser.parse_args()
    object_id = args.object_id

    with MongoConnection(**db_config) as con:
        # last_run = con.col.find(sort=[("_id", pymongo.DESCENDING)])
        # NOTE how to distinguish the runs?
        # jcop4 = con.col.find_one({"_id": ObjectId("637b9d9eff18ad3f62d380e6")})
        jcop4 = con.col.find_one({"_id": ObjectId(object_id.replace(" ", ""))})
        # for run in runs:
        #     try:
        #         print(list(run["analysis-results"].keys()))
        #     except (AttributeError, KeyError):
        #         continue

    crypto_table = defaultdict(dict)
    security_table = defaultdict(dict)

    for key, data in jcop4["analysis-results"].items():
        if key.startswith("crypto_pkg"):
            # crypto_pkg_jc221_javacardx_crypto_1_2-jc221
            found = re.search(r"javacardx_crypto_(?P<major>\d)_(?P<minor>\d)", key)
            major = found.group("major")
            minor = found.group("minor")
            # FIXME verify data["results"][0] is the `install` stage indeed (it should)
            crypto_table[f"{major}.{minor}"][data["sdk_version"]] = (
                1 if data["results"][0]["success"] else 0
            )
        if key.startswith("security_pkg"):
            found = re.search(r"javacard_security_(?P<major>\d)_(?P<minor>\d)", key)
            major = found.group("major")
            minor = found.group("minor")
            security_table[f"{major}.{minor}"][data["sdk_version"]] = (
                1 if data["results"][0]["success"] else 0
            )

    print(crypto_table)
    cr_table = []
    for row, cols in crypto_table.items():
        cr_table.append(list(cols.values()))

    fig = px.imshow(cr_table)
    fig.show()

    print(security_table)
    sc_table = []
    for row, cols in security_table.items():
        sc_table.append(list(cols.values()))

    fig = px.imshow(sc_table)
    fig.show()


if __name__ == "__main__":
    main()
