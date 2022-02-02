"""Call getRevisionsCount for the given padid"""

import json
from argparse import ArgumentParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


def main(args):
    p = ArgumentParser("call getRevisionsCount for the given padid")
    p.add_argument("padid", help="the padid")
    p.add_argument(
        "--padinfo",
        default=".etherpump/settings.json",
        help="settings, default: .etherdump/settings.json",
    )
    p.add_argument("--showurl", default=False, action="store_true")
    args = p.parse_args(args)

    with open(args.padinfo) as f:
        info = json.load(f)
    apiurl = info.get("apiurl")
    data = {}
    data["apikey"] = info["apikey"]
    data["padID"] = args.padid
    requesturl = apiurl + "getRevisionsCount?" + urlencode(data)
    if args.showurl:
        print(requesturl)
    else:
        results = json.load(urlopen(requesturl))["data"]["revisions"]
        print(results)
