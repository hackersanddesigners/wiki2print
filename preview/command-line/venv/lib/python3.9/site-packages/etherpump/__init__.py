#!/usr/bin/env python3
import os
import sys

DATAPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

__VERSION__ = "0.0.20"


def subcommands():
    """List all sub-commands for the `--help` output."""
    output = []

    subcommands = [
        "creatediffhtml",
        "deletepad",
        "dumpcsv",
        "gethtml",
        "gettext",
        "index",
        "init",
        "list",
        "listauthors",
        "publication",
        "pull",
        "revisionscount",
        "sethtml",
        "settext",
        "showmeta",
    ]

    for subcommand in subcommands:
        try:
            # http://stackoverflow.com/questions/301134/dynamic-module-import-in-python
            doc = __import__(
                "etherpump.commands.%s" % subcommand,
                fromlist=["etherdump.commands"],
            ).__doc__
        except ModuleNotFoundError:
            doc = ""
        output.append(f"    {subcommand}: {doc}")

    output.sort()

    return "\n".join(output)


usage = """
         _
        | |
  _ _|_ | |     _   ,_     _          _  _  _     _
 |/  |  |/ \   |/  /  |  |/ \_|   |  / |/ |/ |  |/ \_
 |__/|_/|   |_/|__/   |_/|__/  \_/|_/  |  |  |_/|__/
                        /|                     /|
                        \|                     \|
Usage:
    etherpump CMD

where CMD could be:
{}

For more information on each command try:
    etherpump CMD --help""".format(
    subcommands()
)


def main():
    try:
        cmd = sys.argv[1]
        if cmd.startswith("-"):
            args = sys.argv
        else:
            args = sys.argv[2:]

        if len(sys.argv) < 3:
            if any(arg in args for arg in ["--help", "-h"]):
                print(usage)
                sys.exit(0)
            elif any(arg in args for arg in ["--version", "-v"]):
                print("etherpump {}".format(__VERSION__))
                sys.exit(0)

    except IndexError:
        print(usage)
        sys.exit(0)

    try:
        # http://stackoverflow.com/questions/301134/dynamic-module-import-in-python
        cmdmod = __import__(
            "etherpump.commands.%s" % cmd, fromlist=["etherdump.commands"]
        )
        cmdmod.main(args)
    except ImportError as e:
        print(
            "Error performing command '{0}'\n(python said: {1})\n".format(
                cmd, e
            )
        )
        print(usage)
