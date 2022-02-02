"""Update meta data files for those that have changed"""
import os
from argparse import ArgumentParser
from urllib.parse import urlencode

from .common import *  # noqa

"""
status (meta):
    Update meta data files for those that have changed.
    Check for changed pads by looking at revisions & comparing to existing


design decisions...
ok based on the fact that only the txt file is pushable (via setText)
it makes sense to give this file "primacy" ... ie to put the other forms
(html, diff.html) in a special place (if created at all). Otherwise this
complicates the "syncing" idea....

"""


class PadItemException(Exception):
    pass


class PadItem:
    def __init__(self, padid=None, path=None, padexists=False):
        self.padexists = padexists
        if padid and path:
            raise PadItemException("only give padid or path")
        if not (padid or path):
            raise PadItemException("either padid or path must be specified")
        if padid:
            self.padid = padid
            self.path = padpath(padid, group_path="g")
        else:
            self.path = path
            self.padid = padpath2id(path)

    @property
    def status(self):
        if self.fileexists:
            if self.padexists:
                return "S"
            else:
                return "F"
        elif self.padexists:
            return "P"
        else:
            return "?"

    @property
    def fileexists(self):
        return os.path.exists(self.path)


def ignore_p(path, settings=None):
    if path.startswith("."):
        return True


def main(args):
    p = ArgumentParser(
        "Check for pads that have changed since last sync (according to .meta.json)"
    )
    # p.add_argument("padid", nargs="*", default=[])
    p.add_argument(
        "--padinfo",
        default=".etherpump/settings.json",
        help="settings, default: .etherdump/settings.json",
    )
    p.add_argument(
        "--zerorevs",
        default=False,
        action="store_true",
        help="include pads with zero revisions, default: False (i.e. pads with no revisions are skipped)",
    )
    p.add_argument(
        "--pub",
        default=".",
        help="folder to store files for public pads, default: pub",
    )
    p.add_argument(
        "--group",
        default="g",
        help="folder to store files for group pads, default: g",
    )
    p.add_argument(
        "--skip",
        default=None,
        type=int,
        help="skip this many items, default: None",
    )
    p.add_argument(
        "--meta",
        default=False,
        action="store_true",
        help="download meta to PADID.meta.json, default: False",
    )
    p.add_argument(
        "--text",
        default=False,
        action="store_true",
        help="download text to PADID.txt, default: False",
    )
    p.add_argument(
        "--html",
        default=False,
        action="store_true",
        help="download html to PADID.html, default: False",
    )
    p.add_argument(
        "--dhtml",
        default=False,
        action="store_true",
        help="download dhtml to PADID.dhtml, default: False",
    )
    p.add_argument(
        "--all",
        default=False,
        action="store_true",
        help="download all files (meta, text, html, dhtml), default: False",
    )
    args = p.parse_args(args)

    info = loadpadinfo(args.padinfo)
    data = {}
    data["apikey"] = info["apikey"]

    padsbypath = {}

    # listAllPads
    padids = getjson(info["apiurl"] + "listAllPads?" + urlencode(data))["data"][
        "padIDs"
    ]
    padids.sort()
    for padid in padids:
        pad = PadItem(padid=padid, padexists=True)
        padsbypath[pad.path] = pad

    files = os.listdir(args.pub)
    files = [x for x in files if not ignore_p(x)]
    files.sort()
    for p in files:
        pad = padsbypath.get(p)
        if not pad:
            pad = PadItem(path=p)
            padsbypath[pad.path] = pad

    pads = list(padsbypath.values())
    pads.sort(key=lambda x: (x.status, x.padid))

    curstat = None
    for p in pads:
        if p.status != curstat:
            curstat = p.status
            if curstat == "F":
                print("New/changed files")
            elif curstat == "P":
                print("New/changed pads")
            elif curstat == ".":
                print("Up to date")
        print("   ", p.status, p.padid)
