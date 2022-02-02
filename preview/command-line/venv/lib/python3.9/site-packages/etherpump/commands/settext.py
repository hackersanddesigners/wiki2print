"""Calls the getText API function for the given padid"""

import json
import sys
from argparse import ArgumentParser
from urllib.parse import urlencode
from urllib.request import urlopen

import requests

LIMIT_BYTES = 100 * 1000


def main(args):
    p = ArgumentParser("calls the getText API function for the given padid")
    p.add_argument("padid", help="the padid")
    p.add_argument(
        "--text", default=None, help="text, default: read from stdin"
    )
    p.add_argument(
        "--padinfo",
        default=".etherpump/settings.json",
        help="settings, default: .etherdump/settings.json",
    )
    p.add_argument("--showurl", default=False, action="store_true")
    # p.add_argument("--format", default="text", help="output format, can be: text, json; default: text")
    p.add_argument(
        "--create",
        default=False,
        action="store_true",
        help="flag to create pad if necessary",
    )
    p.add_argument(
        "--limit",
        default=False,
        action="store_true",
        help="limit text to 100k (etherpad limit)",
    )
    args = p.parse_args(args)

    with open(args.padinfo) as f:
        info = json.load(f)
    apiurl = info.get("apiurl")
    # apiurl = "{0[protocol]}://{0[hostname]}:{0[port]}{0[apiurl]}{0[apiversion]}/".format(info)
    data = {}
    data["apikey"] = info["apikey"]
    data["padID"] = args.padid  # is utf-8 encoded

    createPad = False
    if args.create:
        requesturl = apiurl + "getRevisionsCount?" + urlencode(data)
        results = json.load(urlopen(requesturl))
        # print (json.dumps(results, indent=2))
        if results["code"] != 0:
            createPad = True

    if args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    if len(text) > LIMIT_BYTES and args.limit:
        print("limiting", len(text), LIMIT_BYTES)
        text = text[:LIMIT_BYTES]

    data["text"] = text

    if createPad:
        requesturl = apiurl + "createPad"
    else:
        requesturl = apiurl + "setText"

    if args.showurl:
        print(requesturl)
    results = requests.post(
        requesturl, params=data
    )  # json.load(urlopen(requesturl))
    results = json.loads(results.text)
    if results["code"] != 0:
        print(
            "setText: ERROR ({0}) on pad {1}: {2}".format(
                results["code"], args.padid, results["message"]
            )
        )
        # json.dumps(results, indent=2)
