"""Generate a single document from etherpumps using a template"""
import json
import os
import re
import sys
import time
from argparse import ArgumentParser
from datetime import datetime
from urllib.parse import urlparse, urlunparse

import dateutil.parser
import pypandoc
from jinja2 import Environment, FileSystemLoader

from etherpump.commands.common import *  # noqa

"""
publication:
    Generate a single document from etherpumps using a template.

    Built-in templates: publication.html

"""


def group(items, key=lambda x: x):
    """ returns a list of lists, of items grouped by a key function """
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


# def base (x):
#     return re.sub(r"(\.raw\.html)|(\.diff\.html)|(\.meta\.json)|(\.raw\.txt)$", "", x)


def splitextlong(x):
    """ split "long" extensions, i.e. foo.bar.baz => ('foo', '.bar.baz') """
    m = re.search(r"^(.*?)(\..*)$", x)
    if m:
        return m.groups()
    else:
        return x, ""


def base(x):
    return splitextlong(x)[0]


def excerpt(t, chars=25):
    if len(t) > chars:
        t = t[:chars] + "..."
    return t


def absurl(url, base=None):
    if not url.startswith("http"):
        return base + url
    return url


def url_base(url):
    (scheme, netloc, path, params, query, fragment) = urlparse(url)
    path, _ = os.path.split(path.lstrip("/"))
    ret = urlunparse((scheme, netloc, path, None, None, None))
    if ret:
        ret += "/"
    return ret


def datetimeformat(t, format="%Y-%m-%d %H:%M:%S"):
    if type(t) == str:
        dt = dateutil.parser.parse(t)
        return dt.strftime(format)
    else:
        return time.strftime(format, time.localtime(t))


def main(args):
    p = ArgumentParser("Convert dumped files to a document via a template.")

    p.add_argument("input", nargs="+", help="Files to list (.meta.json files)")

    p.add_argument(
        "--templatepath",
        default=None,
        help="path to find templates, default: built-in",
    )
    p.add_argument(
        "--template",
        default="publication.html",
        help="template name, built-ins include publication.html; default: publication.html",
    )
    p.add_argument(
        "--padinfo",
        default=".etherpump/settings.json",
        help="settings, default: ./.etherdump/settings.json",
    )
    # p.add_argument("--zerorevs", default=False, action="store_true", help="include pads with zero revisions, default: False (i.e. pads with no revisions are skipped)")

    p.add_argument(
        "--order",
        default="padid",
        help="order, possible values: padid, pad (no group name), lastedited, (number of) authors, revisions, default: padid",
    )
    p.add_argument(
        "--reverse",
        default=False,
        action="store_true",
        help="reverse order, default: False (reverse chrono)",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="limit to number of items, default: 0 (no limit)",
    )
    p.add_argument(
        "--skip",
        default=None,
        type=int,
        help="skip this many items, default: None",
    )

    p.add_argument(
        "--content",
        default=False,
        action="store_true",
        help="rss: include (full) content tag, default: False",
    )
    p.add_argument(
        "--link",
        default="diffhtml,html,text",
        help="link variable will be to this version, can be comma-delim list, use first avail, default: diffhtml,html,text",
    )
    p.add_argument(
        "--linkbase",
        default=None,
        help="base url to use for links, default: try to use the feedurl",
    )
    p.add_argument("--output", default=None, help="output, default: stdout")

    p.add_argument(
        "--files",
        default=False,
        action="store_true",
        help="include files (experimental)",
    )

    pg = p.add_argument_group("template variables")
    pg.add_argument(
        "--feedurl",
        default="feed.xml",
        help="rss: to use as feeds own (self) link, default: feed.xml",
    )
    pg.add_argument(
        "--siteurl",
        default=None,
        help="rss: to use as channel's site link, default: the etherpad url",
    )
    pg.add_argument(
        "--title",
        default="etherpump",
        help="title for document or rss feed channel title, default: etherdump",
    )
    pg.add_argument(
        "--description",
        default="",
        help="rss: channel description, default: empty",
    )
    pg.add_argument(
        "--language", default="en-US", help="rss: feed language, default: en-US"
    )
    pg.add_argument(
        "--updatePeriod",
        default="daily",
        help="rss: updatePeriod, possible values: hourly, daily, weekly, monthly, yearly; default: daily",
    )
    pg.add_argument(
        "--updateFrequency",
        default=1,
        type=int,
        help="rss: update frequency within the update period (where 2 would mean twice per period); default: 1",
    )
    pg.add_argument(
        "--generator",
        default="https://git.vvvvvvaria.org/varia/etherpump",
        help="generator, default: https://git.vvvvvvaria.org/varia/etherdump",
    )
    pg.add_argument(
        "--timestamp",
        default=None,
        help="timestamp, default: now (e.g. 2015-12-01 12:30:00)",
    )
    pg.add_argument("--next", default=None, help="next link, default: None)")
    pg.add_argument("--prev", default=None, help="prev link, default: None")

    args = p.parse_args(args)

    tmpath = args.templatepath
    # Default path for template is the built-in data/templates
    if tmpath == None:
        tmpath = os.path.split(os.path.abspath(__file__))[0]
        tmpath = os.path.split(tmpath)[0]
        tmpath = os.path.join(tmpath, "data", "templates")

    env = Environment(loader=FileSystemLoader(tmpath))
    env.filters["excerpt"] = excerpt
    env.filters["datetimeformat"] = datetimeformat
    template = env.get_template(args.template)

    info = loadpadinfo(args.padinfo)

    inputs = args.input
    inputs.sort()

    # Use "base" to strip (longest) extensions
    # inputs = group(inputs, base)

    def wrappath(p):
        path = "./{0}".format(p)
        ext = os.path.splitext(p)[1][1:]
        return {"url": path, "path": path, "code": 200, "type": ext}

    def metaforpaths(paths):
        ret = {}
        pid = base(paths[0])
        ret["pad"] = ret["padid"] = pid
        ret["versions"] = [wrappath(x) for x in paths]
        lastedited = None
        for p in paths:
            mtime = os.stat(p).st_mtime
            if lastedited == None or mtime > lastedited:
                lastedited = mtime
        ret["lastedited_iso"] = datetime.fromtimestamp(lastedited).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        ret["lastedited_raw"] = mtime
        return ret

    def loadmeta(p):
        # Consider a set of grouped files
        # Otherwise, create a "dummy" one that wraps all the files as versions
        if p.endswith(".meta.json"):
            with open(p) as f:
                return json.load(f)
        # if there is a .meta.json, load it & MERGE with other files
        # if ret:
        #     # TODO: merge with other files
        #     for p in paths:
        #         if "./"+p not in ret['versions']:
        #             ret['versions'].append(wrappath(p))
        #     return ret
        # else:
        #     return metaforpaths(paths)

    def fixdates(padmeta):
        d = dateutil.parser.parse(padmeta["lastedited_iso"])
        padmeta["lastedited"] = d
        padmeta["lastedited_822"] = d.strftime("%a, %d %b %Y %H:%M:%S +0000")
        return padmeta

    pads = list(map(loadmeta, inputs))
    pads = [x for x in pads if x != None]
    pads = list(map(fixdates, pads))
    args.pads = list(pads)

    def could_have_base(x, y):
        return x == y or (x.startswith(y) and x[len(y) :].startswith("."))

    def get_best_pad(x):
        for pb in padbases:
            p = pads_by_base[pb]
            if could_have_base(x, pb):
                return p

    def has_version(padinfo, path):
        return [
            x
            for x in padinfo["versions"]
            if "path" in x and x["path"] == "./" + path
        ]

    if args.files:
        inputs = args.input
        inputs.sort()
        removelist = []

        pads_by_base = {}
        for p in args.pads:
            # print ("Trying padid", p['padid'], file=sys.stderr)
            padbase = os.path.splitext(p["padid"])[0]
            pads_by_base[padbase] = p
        padbases = list(pads_by_base.keys())
        # SORT THEM LONGEST FIRST TO ensure that LONGEST MATCHES MATCH
        padbases.sort(key=lambda x: len(x), reverse=True)
        # print ("PADBASES", file=sys.stderr)
        # for pb in padbases:
        #     print ("  ", pb, file=sys.stderr)
        print("pairing input files with pads", file=sys.stderr)
        for x in inputs:
            # pair input with a pad if possible
            xbasename = os.path.basename(x)
            p = get_best_pad(xbasename)
            if p:
                if not has_version(p, x):
                    print(
                        "Grouping file {0} with pad {1}".format(x, p["padid"]),
                        file=sys.stderr,
                    )
                    p["versions"].append(wrappath(x))
                else:
                    print(
                        "Skipping existing version {0} ({1})...".format(
                            x, p["padid"]
                        ),
                        file=sys.stderr,
                    )
                removelist.append(x)
        # Removed Matches files
        for x in removelist:
            inputs.remove(x)
        print("Remaining files:", file=sys.stderr)
        for x in inputs:
            print(x, file=sys.stderr)
        print(file=sys.stderr)
        # Add "fake" pads for remaining files
        for x in inputs:
            args.pads.append(metaforpaths([x]))

    if args.timestamp == None:
        args.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    padurlbase = re.sub(r"api/1.2.9/$", "p/", info["apiurl"])
    args.siteurl = args.siteurl or padurlbase
    args.utcnow = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

    # order items & apply limit
    if args.order == "lastedited":
        args.pads.sort(
            key=lambda x: x.get("lastedited_iso"), reverse=args.reverse
        )
    elif args.order == "pad":
        args.pads.sort(key=lambda x: x.get("pad"), reverse=args.reverse)
    elif args.order == "padid":
        args.pads.sort(key=lambda x: x.get("padid"), reverse=args.reverse)
    elif args.order == "revisions":
        args.pads.sort(key=lambda x: x.get("revisions"), reverse=args.reverse)
    elif args.order == "authors":
        args.pads.sort(
            key=lambda x: len(x.get("authors")), reverse=args.reverse
        )
    elif args.order == "custom":

        # TODO: make this list non-static, but a variable that can be given from the CLI

        customorder = [
            "nooo.relearn.preamble",
            "nooo.relearn.activating.the.archive",
            "nooo.relearn.call.for.proposals",
            "nooo.relearn.call.for.proposals-proposal-footnote",
            "nooo.relearn.colophon",
        ]
        order = []
        for x in customorder:
            for pad in args.pads:
                if pad["padid"] == x:
                    order.append(pad)
        args.pads = order
    else:
        raise Exception("That ordering is not implemented!")

    if args.limit:
        args.pads = args.pads[: args.limit]

    # add versions_by_type, add in full text
    # add link (based on args.link)
    linkversions = args.link.split(",")
    linkbase = args.linkbase or url_base(args.feedurl)
    # print ("linkbase", linkbase, args.linkbase, args.feedurl)

    for p in args.pads:
        versions_by_type = {}
        p["versions_by_type"] = versions_by_type
        for v in p["versions"]:
            t = v["type"]
            versions_by_type[t] = v

        if "text" in versions_by_type:
            # try:
            with open(versions_by_type["text"]["path"]) as f:
                content = f.read()
                # print('content:', content)
                # [Relearn] Add pandoc command here?
                html = pypandoc.convert_text(content, "html", format="md")
                # print('html:', html)
                p["text"] = html
            # except FileNotFoundError:
            # p['text'] = 'ERROR'

        # ADD IN LINK TO PAD AS "link"
        for v in linkversions:
            if v in versions_by_type:
                vdata = versions_by_type[v]
                try:
                    if v == "pad" or os.path.exists(vdata["path"]):
                        p["link"] = absurl(vdata["url"], linkbase)
                        break
                except KeyError as e:
                    pass

    if args.output:
        with open(args.output, "w") as f:
            print(template.render(vars(args)), file=f)
    else:
        print(template.render(vars(args)))
