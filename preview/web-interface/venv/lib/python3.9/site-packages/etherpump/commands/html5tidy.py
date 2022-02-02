#!/usr/bin/env python3


import os
import sys
from argparse import ArgumentParser
from xml.etree import ElementTree as ET

from html5lib import parse


def etree_indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            etree_indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def get_link_type(url):
    lurl = url.lower()
    if lurl.endswith(".html") or lurl.endswith(".htm"):
        return "text/html"
    elif lurl.endswith(".txt"):
        return "text/plain"
    elif lurl.endswith(".rss"):
        return "application/rss+xml"
    elif lurl.endswith(".atom"):
        return "application/atom+xml"
    elif lurl.endswith(".json"):
        return "application/json"
    elif lurl.endswith(".js") or lurl.endswith(".jsonp"):
        return "text/javascript"


def pluralize(x):
    if type(x) == list or type(x) == tuple:
        return x
    else:
        return (x,)


def html5tidy(
    doc, charset="utf-8", title=None, scripts=None, links=None, indent=False
):
    if scripts:
        script_srcs = [x.attrib.get("src") for x in doc.findall(".//script")]
        for src in pluralize(scripts):
            if src not in script_srcs:
                script = ET.SubElement(doc.find(".//head"), "script", src=src)
                script_srcs.append(src)

    if links:
        existinglinks = {}
        for elt in doc.findall(".//link"):
            href = elt.attrib.get("href")
            if href:
                existinglinks[href] = elt
        for link in links:
            linktype = link.get("type") or get_link_type(link["href"])
            if link["href"] in existinglinks:
                elt = existinglinks[link["href"]]
                elt.attrib["rel"] = link["rel"]
            else:
                elt = ET.SubElement(
                    doc.find(".//head"),
                    "link",
                    href=link["href"],
                    rel=link["rel"],
                )
            if linktype:
                elt.attrib["type"] = linktype
            if "title" in link:
                elt.attrib["title"] = link["title"]

    if charset:
        meta_charsets = [
            x.attrib.get("charset")
            for x in doc.findall(".//meta")
            if x.attrib.get("charset") != None
        ]
        if not meta_charsets:
            meta = ET.SubElement(doc.find(".//head"), "meta", charset=charset)

    if title != None:
        titleelt = doc.find(".//title")
        if not titleelt:
            titleelt = ET.SubElement(doc.find(".//head"), "title")
        titleelt.text = title

    if indent:
        etree_indent(doc)
    return doc


def main(args):
    p = ArgumentParser("")
    p.add_argument("input", nargs="?", default=None)
    p.add_argument("--indent", default=False, action="store_true")
    p.add_argument(
        "--mogrify",
        default=False,
        action="store_true",
        help="modify file in place",
    )
    p.add_argument(
        "--method",
        default="html",
        help="method, default: html, values: html, xml, text",
    )
    p.add_argument("--output", default=None, help="")
    p.add_argument("--title", default=None, help="ensure/add title tag in head")
    p.add_argument(
        "--charset", default="utf-8", help="ensure/add meta tag with charset"
    )
    p.add_argument(
        "--script", action="append", default=[], help="ensure/add script tag"
    )
    # <link>s, see https://www.w3.org/TR/html5/links.html#links
    p.add_argument(
        "--stylesheet",
        action="append",
        default=[],
        help="ensure/add style link",
    )
    p.add_argument(
        "--alternate",
        action="append",
        default=[],
        nargs="+",
        help="ensure/add alternate links (optionally followed by a title and type)",
    )
    p.add_argument(
        "--next",
        action="append",
        default=[],
        nargs="+",
        help="ensure/add alternate link",
    )
    p.add_argument(
        "--prev",
        action="append",
        default=[],
        nargs="+",
        help="ensure/add alternate link",
    )
    p.add_argument(
        "--search",
        action="append",
        default=[],
        nargs="+",
        help="ensure/add search link",
    )
    p.add_argument(
        "--rss",
        action="append",
        default=[],
        nargs="+",
        help="ensure/add alternate link of type application/rss+xml",
    )
    p.add_argument(
        "--atom",
        action="append",
        default=[],
        nargs="+",
        help="ensure/add alternate link of type application/atom+xml",
    )

    args = p.parse_args(args)
    links = []

    def add_links(links, items, rel, _type=None):
        for href in items:
            d = {}
            d["rel"] = rel
            if _type:
                d["type"] = _type

            if type(href) == list:
                if len(href) == 1:
                    d["href"] = href[0]
                elif len(href) == 2:
                    d["href"] = href[0]
                    d["title"] = href[1]
                elif len(href) == 3:
                    d["href"] = href[0]
                    d["title"] = href[1]
                    d["type"] = href[2]
                else:
                    continue
            else:
                d["href"] = href

            links.append(d)

    for rel in ("stylesheet", "alternate", "next", "prev", "search"):
        add_links(links, getattr(args, rel), rel)
    for item in args.rss:
        add_links(links, item, rel="alternate", _type="application/rss+xml")
    for item in args.atom:
        add_links(links, item, rel="alternate", _type="application/atom+xml")

    # INPUT
    if args.input:
        fin = open(args.input)
    else:
        fin = sys.stdin

    doc = parse(fin, treebuilder="etree", namespaceHTMLElements=False)
    if fin != sys.stdin:
        fin.close()
    html5tidy(
        doc,
        scripts=args.script,
        links=links,
        title=args.title,
        indent=args.indent,
    )

    # OUTPUT
    tmppath = None
    if args.output:
        fout = open(args.output, "w")
    elif args.mogrify:
        tmppath = args.input + ".tmp"
        fout = open(tmppath, "w")
    else:
        fout = sys.stdout

    print(ET.tostring(doc, method=args.method, encoding="unicode"), file=fout)

    if fout != sys.stdout:
        fout.close()

    if tmppath:
        os.rename(args.input, args.input + "~")
        os.rename(tmppath, args.input)


if __name__ == "__main__":
    main(sys.argv)
