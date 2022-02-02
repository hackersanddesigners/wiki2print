"""Dumps a CSV of all pads"""

import json
import re
import sys
from argparse import ArgumentParser
from csv import writer
from datetime import datetime
from math import ceil, floor
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

"""
Dumps a CSV of all pads with columns
padid, groupid, revisions, lastedited, author_ids

    padids have their group name trimmed
    groupid is without (g.  $)
    revisions is an integral number of edits
    lastedited is ISO8601 formatted
    author_ids is a space delimited list of internal author IDs
"""

groupnamepat = re.compile(r"^g\.(\w+)\$")

out = writer(sys.stdout)


def jsonload(url):
    f = urlopen(url)
    data = f.read()
    f.close()
    return json.loads(data)


def main(args):
    p = ArgumentParser("outputs a CSV of information all all pads")
    p.add_argument(
        "--padinfo",
        default=".etherpump/settings.json",
        help="settings, default: .etherdump/settings.json",
    )
    p.add_argument(
        "--zerorevs",
        default=False,
        action="store_true",
        help="include pads with zero revisions, default: False",
    )
    args = p.parse_args(args)

    with open(args.padinfo) as f:
        info = json.load(f)
    apiurl = info.get("apiurl")
    data = {}
    data["apikey"] = info["apikey"]
    requesturl = apiurl + "listAllPads?" + urlencode(data)

    padids = jsonload(requesturl)["data"]["padIDs"]
    padids.sort()
    numpads = len(padids)
    maxmsglen = 0
    count = 0
    out.writerow(("padid", "groupid", "lastedited", "revisions", "author_ids"))
    for i, padid in enumerate(padids):
        p = float(i) / numpads
        percentage = int(floor(p * 100))
        bars = int(ceil(p * 20))
        bar = ("*" * bars) + ("-" * (20 - bars))
        msg = "\r{0} {1}/{2} {3}... ".format(bar, (i + 1), numpads, padid)
        if len(msg) > maxmsglen:
            maxmsglen = len(msg)
        sys.stderr.write("\r{0}".format(" " * maxmsglen))
        sys.stderr.write(msg)
        sys.stderr.flush()
        m = groupnamepat.match(padid)
        if m:
            groupname = m.group(1)
            padidnogroup = padid[m.end() :]
        else:
            groupname = ""
            padidnogroup = padid

        data["padID"] = padid
        revisions = jsonload(apiurl + "getRevisionsCount?" + urlencode(data))[
            "data"
        ]["revisions"]
        if (revisions == 0) and not args.zerorevs:
            continue

        lastedited_raw = jsonload(apiurl + "getLastEdited?" + urlencode(data))[
            "data"
        ]["lastEdited"]
        lastedited_iso = datetime.fromtimestamp(
            int(lastedited_raw) / 1000
        ).isoformat()
        author_ids = jsonload(apiurl + "listAuthorsOfPad?" + urlencode(data))[
            "data"
        ]["authorIDs"]
        author_ids = " ".join(author_ids)
        out.writerow(
            (padidnogroup, groupname, revisions, lastedited_iso, author_ids)
        )
        count += 1

    print("\nWrote {0} rows...".format(count), file=sys.stderr)
