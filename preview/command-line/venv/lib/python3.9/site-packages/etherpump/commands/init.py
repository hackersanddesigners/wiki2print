"""Initialize an etherpump folder"""

import json
import os
import sys
from argparse import ArgumentParser
from urllib.parse import urlencode, urlparse, urlunparse
from urllib.request import HTTPError, URLError, urlopen


def get_api(url, cmd=None, data=None, verbose=False):
    try:
        useurl = url + cmd
        if data:
            useurl += "?" + urlencode(data)
        if verbose:
            print("trying", useurl, file=sys.stderr)
        resp = urlopen(useurl).read()
        resp = resp.decode("utf-8")
        resp = json.loads(resp)
        if "code" in resp and "message" in resp:
            return resp
    except ValueError as e:
        if verbose:
            print("  ValueError", e, file=sys.stderr)
        return
    except HTTPError as e:
        if verbose:
            print("  HTTPError", e, file=sys.stderr)
        if e.code == 401:
            # Unauthorized is how the API responds to an incorrect API key
            return {"code": 401, "message": e}


def tryapiurl(url, verbose=False):
    """
    Try to use url as api, correcting if possible.
    Returns corrected / normalized URL, or None if not possible
    """
    try:
        scheme, netloc, path, params, query, fragment = urlparse(url)
        if scheme == "":
            url = "http://" + url
        scheme, netloc, path, params, query, fragment = urlparse(url)
        params, query, fragment = ("", "", "")
        path = path.strip("/")
        # 1. try directly...
        apiurl = (
            urlunparse((scheme, netloc, path, params, query, fragment)) + "/"
        )
        if get_api(apiurl, "listAllPads", verbose=verbose):
            return apiurl
        # 2. try with += api/1.2.9
        path = os.path.join(path, "api", "1.2.9") + "/"
        apiurl = urlunparse((scheme, netloc, path, params, query, fragment))
        if get_api(apiurl, "listAllPads", verbose=verbose):
            return apiurl
    except URLError as e:
        print("URLError", e, file=sys.stderr)


def main(args):
    p = ArgumentParser("initialize an etherpump folder")
    p.add_argument(
        "arg",
        nargs="*",
        default=[],
        help="optional positional args: path etherpadurl",
    )
    p.add_argument("--path", default=None, help="path to initialize")
    p.add_argument("--padurl", default=None, help="")
    p.add_argument("--apikey", default=None, help="")
    p.add_argument("--verbose", default=False, action="store_true", help="")
    p.add_argument("--reinit", default=False, action="store_true", help="")
    args = p.parse_args(args)

    path = args.path
    if path == None and len(args.arg):
        path = args.arg[0]
    if not path:
        path = "."

    edpath = os.path.join(path, ".etherpump")
    try:
        os.makedirs(edpath)
    except OSError:
        pass

    padinfo = {}
    padinfopath = os.path.join(edpath, "settings.json")
    try:
        with open(padinfopath) as f:
            padinfo = json.load(f)
        if not args.reinit:
            print("Folder already initialized. Use --reinit to reset settings")
            sys.exit(0)
    except IOError:
        pass
    except ValueError:
        # bad json file, reset it
        pass

    apiurl = args.padurl
    while True:
        if apiurl:
            apiurl = tryapiurl(apiurl, verbose=args.verbose)
        if apiurl:
            # print ("Got APIURL: {0}".format(apiurl))
            break
        apiurl = input(
            "Please type the URL of the etherpad (e.g. https://pad.vvvvvvaria.org): "
        ).strip()
    padinfo["apiurl"] = apiurl
    apikey = args.apikey
    while True:
        if apikey:
            resp = get_api(
                apiurl, "listAllPads", {"apikey": apikey}, verbose=args.verbose
            )
            if resp and resp["code"] == 0:
                # print ("GOOD")
                break
            else:
                print("bad")
        print(
            "The APIKEY is the contents of the file APIKEY.txt in the etherpad folder",
            file=sys.stderr,
        )
        apikey = input("Please paste the APIKEY: ").strip()
    padinfo["apikey"] = apikey

    with open(padinfopath, "w") as f:
        json.dump(padinfo, f, indent=2)
