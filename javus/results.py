#!/usr/bin/env python3

import re

from collections import defaultdict

from javus.utils import MongoConnection, AttackConfigParser
from javus.settings import ATTACKS

import configparser

# FIXME load from config file
db_config = {
    "database": "javacard-analysis",
    "host": "localhost",
    "port": "27017",
}


def aggregate_attacks_over_all_runs(atr):
    with MongoConnection(**db_config) as con:
        runs = con.col.find(
            {"analysis-results": {"$exists": True}, "card.atr": {"$eq": atr}}
        )

    attacks_dct = defaultdict(set)
    for r in runs:
        _id = r["_id"]
        attacks = list(r["analysis-results"].keys())
        for attack in attacks:
            name, sdk = attack.split("-")
            attacks_dct[name].add(sdk)

    for attack, sdks in attacks_dct.items():
        at_config = AttackConfigParser()
        at_config.read(ATTACKS / attack / "config.ini")
        print(f"{attack}: {len(sdks)}/{len(at_config.get_supported_versions())}")


if __name__ == "__main__":
    athena_atr = "3B D5 18 FF 81 91 FE 1F C3 80 73 C8 21 13 09"
    aggregate_attacks_over_all_runs(atr=athena_atr)
