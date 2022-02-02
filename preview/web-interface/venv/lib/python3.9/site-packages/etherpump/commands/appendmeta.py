#!/usr/bin/env python

import json
from argparse import ArgumentParser


def main(args):
    p = ArgumentParser("")
    p.add_argument("input", nargs="+", help="filenames")
    p.add_argument("--indent", type=int, default=2, help="indent")
    args = p.parse_args(args)
    inputs = args.input
    inputs.sort()
    ret = []
    for p in inputs:
        with open(p) as f:
            meta = json.load(f)
            ret.append(meta)

    if args.indent:
        print(json.dumps(ret, indent=args.indent))
    else:
        print(json.dumps(ret))
