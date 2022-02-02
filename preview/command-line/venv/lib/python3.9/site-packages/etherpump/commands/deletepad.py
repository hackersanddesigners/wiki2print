"""Calls the getText API function for the given padid"""

import json
from argparse import ArgumentParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


def main(args):
    p = ArgumentParser("calls the getText API function for the given padid")
    p.add_argument("padid", help="the padid")
    p.add_argument(
        "--padinfo",
        default=".etherpump/settings.json",
        help="settings, default: .etherdump/settings.json",
    )
    p.add_argument("--showurl", default=False, action="store_true")
    p.add_argument(
        "--format",
        default="text",
        help="output format, can be: text, json; default: text",
    )
    args = p.parse_args(args)

    with open(args.padinfo) as f:
        info = json.load(f)
    apiurl = info.get("apiurl")
    data = {}
    data["apikey"] = info["apikey"]
    data["padID"] = args.padid
    requesturl = apiurl + "deletePad?" + urlencode(data)
    if args.showurl:
        print(requesturl)
    else:
        results = json.load(urlopen(requesturl))
        if args.format == "json":
            print(json.dumps(results))
        else:
            if results["data"]:
                print(results["data"]["text"])
