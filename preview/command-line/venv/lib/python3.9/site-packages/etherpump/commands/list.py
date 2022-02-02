"""Call listAllPads and print the results"""

import json
import sys
from argparse import ArgumentParser
from urllib.parse import urlencode, urlparse, urlunparse
from urllib.request import HTTPError, URLError, urlopen

from etherpump.commands.common import getjson


def main(args):
    p = ArgumentParser("call listAllPads and print the results")
    p.add_argument(
        "--padinfo",
        default=".etherpump/settings.json",
        help="settings, default: .etherdump/settings.json",
    )
    p.add_argument("--showurl", default=False, action="store_true")
    p.add_argument(
        "--format",
        default="lines",
        help="output format: lines, json; default lines",
    )
    args = p.parse_args(args)

    with open(args.padinfo) as f:
        info = json.load(f)
    apiurl = info.get("apiurl")
    # apiurl = {0[protocol]}://{0[hostname]}:{0[port]}{0[apiurl]}{0[apiversion]}/".format(info)
    data = {}
    data["apikey"] = info["apikey"]
    requesturl = apiurl + "listAllPads?" + urlencode(data)
    if args.showurl:
        print(requesturl)
    else:
        results = getjson(requesturl)["data"]["padIDs"]
        if args.format == "json":
            print(json.dumps(results))
        else:
            for r in results:
                print(r)
