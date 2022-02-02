"""Call listAuthorsOfPad for the padid"""

import json
from argparse import ArgumentParser
from urllib.parse import urlencode
from urllib.request import urlopen


def main(args):
    p = ArgumentParser("call listAuthorsOfPad for the padid")
    p.add_argument("padid", help="the padid")
    p.add_argument(
        "--padinfo",
        default=".etherpump/settings.json",
        help="settings, default: .etherdump/settings.json",
    )
    p.add_argument("--showurl", default=False, action="store_true")
    p.add_argument(
        "--format",
        default="lines",
        help="output format, can be: lines, json; default: lines",
    )
    args = p.parse_args(args)

    with open(args.padinfo) as f:
        info = json.load(f)
    apiurl = info.get("apiurl")
    data = {}
    data["apikey"] = info["apikey"]
    data["padID"] = args.padid
    requesturl = apiurl + "listAuthorsOfPad?" + urlencode(data)
    if args.showurl:
        print(requesturl)
    else:
        results = json.load(urlopen(requesturl))["data"]["authorIDs"]
        if args.format == "json":
            print(json.dumps(results))
        else:
            for r in results:
                print(r)
