"""Calls the setHTML API function for the given padid"""

import json
import sys
from argparse import ArgumentParser
from urllib.parse import urlencode
from urllib.request import urlopen

import requests

LIMIT_BYTES = 100 * 1000


def main(args):
    p = ArgumentParser("calls the setHTML API function for the given padid")
    p.add_argument("padid", help="the padid")
    p.add_argument(
        "--html", default=None, help="html, default: read from stdin"
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
    #    data = {}
    #    data['apikey'] = info['apikey']
    #    data['padID'] = args.padid # is utf-8 encoded

    createPad = False
    if args.create:
        # check if it's in fact necessary
        requesturl = (
            apiurl
            + "getRevisionsCount?"
            + urlencode({"apikey": info["apikey"], "padID": args.padid})
        )
        results = json.load(urlopen(requesturl))
        print(json.dumps(results, indent=2), file=sys.stderr)
        if results["code"] != 0:
            createPad = True

    if args.html:
        html = args.html
    else:
        html = sys.stdin.read()

    params = {}
    params["apikey"] = info["apikey"]
    params["padID"] = args.padid

    if createPad:
        requesturl = apiurl + "createPad"
        if args.showurl:
            print(requesturl)
        results = requests.post(
            requesturl, params=params, data={"text": ""}
        )  # json.load(urlopen(requesturl))
        results = json.loads(results.text)
        print(json.dumps(results, indent=2))

    if len(html) > LIMIT_BYTES and args.limit:
        print("limiting", len(text), LIMIT_BYTES, file=sys.stderr)
        html = html[:LIMIT_BYTES]

    requesturl = apiurl + "setHTML"
    if args.showurl:
        print(requesturl)
    # params['html'] = html
    results = requests.post(
        requesturl,
        params={"apikey": info["apikey"]},
        data={"apikey": info["apikey"], "padID": args.padid, "html": html},
    )  # json.load(urlopen(requesturl))
    results = json.loads(results.text)
    print(json.dumps(results, indent=2))
