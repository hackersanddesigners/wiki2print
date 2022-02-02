import json
import os
import re
from argparse import ArgumentParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


def group(items, key=lambda x: x):
    ret = []
    keys = {}
    for item in items:
        k = key(item)
        if k not in keys:
            keys[k] = []
        keys[k].append(item)
    for k in sorted(keys):
        keys[k].sort()
        ret.append(keys[k])
    return ret


def main(args):
    p = ArgumentParser("")
    p.add_argument("input", nargs="+", help="filenames")
    args = p.parse_args(args)

    inputs = args.input
    inputs.sort()

    inputs = [x for x in inputs if not os.path.isdir(x)]

    def base(x):
        return re.sub(r"(\.html)|(\.diff\.html)|(\.meta\.json)|(\.txt)$", "", x)

    # from pprint import pprint
    # pprint()
    gg = group(inputs, base)
    for items in gg:
        itembase = base(items[0])
        try:
            os.mkdir(itembase)
        except OSError:
            pass
        for i in items:
            newloc = os.path.join(itembase, i)
            print("'{0}' => '{1}'".format(i, newloc))
            os.rename(i, newloc)
