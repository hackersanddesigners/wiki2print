"""Extract and output selected fields of metadata"""
import json
import re
import sys
from argparse import ArgumentParser

from .common import *  # noqa

"""
Extract and output selected fields of metadata
"""


def main(args):
    p = ArgumentParser(
        "extract & display meta data from a specific .meta.json file, or for a given padid (nb: it still looks for a .meta.json file)"
    )
    p.add_argument("--path", default=None, help="read from a meta.json file")
    p.add_argument("--padid", default=None, help="read meta for this padid")
    p.add_argument(
        "--format", default="{padid}", help="format str, default: {padid}"
    )
    args = p.parse_args(args)

    path = args.path
    if not path and args.padid:
        path = padpath(args.padid) + ".meta.json"

    if not path:
        print("Must specify either --path or --padid")
        sys.exit(-1)

    with open(path) as f:
        meta = json.load(f)

    formatstr = args.format.decode("utf-8")
    formatstr = re.sub(r"{(\w+)}", r"{0[\1]}", formatstr)
    print(formatstr.format(meta))
