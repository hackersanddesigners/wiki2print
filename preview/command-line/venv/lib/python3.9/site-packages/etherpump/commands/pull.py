"""Check for pads that have changed since last sync (according to .meta.json)"""
import json
import os
import re
import sys
import time
from argparse import ArgumentParser
from datetime import datetime
from fnmatch import fnmatch
from urllib.parse import quote, urlencode
from urllib.request import HTTPError
from xml.etree import ElementTree as ET

import asks
import html5lib
import trio

from etherpump.commands.common import *  # noqa
from etherpump.commands.html5tidy import html5tidy

"""
pull(meta):
        Update meta data files for those that have changed.
        Check for changed pads by looking at revisions & comparing to existing
todo...
use/prefer public interfaces ? (export functions)
"""

# Note(decentral1se): simple globals counting
skipped, saved = 0, 0


async def try_deleting(files):
    for f in files:
        try:
            path = trio.Path(f)
            if os.path.exists(path):
                await path.rmdir()
        except Exception as exception:
            print("PANIC: {}".format(exception))


def build_argument_parser(args):
    parser = ArgumentParser(
        "Check for pads that have changed since last sync (according to .meta.json)"
    )
    parser.add_argument("padid", nargs="*", default=[])
    parser.add_argument(
        "--glob", default=False, help="download pads matching a glob pattern"
    )
    parser.add_argument(
        "--padinfo",
        default=".etherpump/settings.json",
        help="settings, default: .etherpump/settings.json",
    )
    parser.add_argument(
        "--zerorevs",
        default=False,
        action="store_true",
        help="include pads with zero revisions, default: False (i.e. pads with no revisions are skipped)",
    )
    parser.add_argument(
        "--pub",
        default="p",
        help="folder to store files for public pads, default: p",
    )
    parser.add_argument(
        "--group",
        default="g",
        help="folder to store files for group pads, default: g",
    )
    parser.add_argument(
        "--skip",
        default=None,
        type=int,
        help="skip this many items, default: None",
    )
    parser.add_argument(
        "--connection",
        default=50,
        type=int,
        help="number of connections to run concurrently",
    )
    parser.add_argument(
        "--meta",
        default=False,
        action="store_true",
        help="download meta to PADID.meta.json, default: False",
    )
    parser.add_argument(
        "--text",
        default=False,
        action="store_true",
        help="download text to PADID.txt, default: False",
    )
    parser.add_argument(
        "--html",
        default=False,
        action="store_true",
        help="download html to PADID.html, default: False",
    )
    parser.add_argument(
        "--dhtml",
        default=False,
        action="store_true",
        help="download dhtml to PADID.diff.html, default: False",
    )
    parser.add_argument(
        "--all",
        default=False,
        action="store_true",
        help="download all files (meta, text, html, dhtml), default: False",
    )
    parser.add_argument(
        "--folder",
        default=False,
        action="store_true",
        help="dump files in a folder named PADID (meta, text, html, dhtml), default: False",
    )
    parser.add_argument(
        "--output",
        default=False,
        action="store_true",
        help="output changed padids on stdout",
    )
    parser.add_argument(
        "--force",
        default=False,
        action="store_true",
        help="reload, even if revisions count matches previous",
    )
    parser.add_argument(
        "--no-raw-ext",
        default=False,
        action="store_true",
        help="save plain text as padname with no (additional) extension",
    )
    parser.add_argument(
        "--fix-names",
        default=False,
        action="store_true",
        help="normalize padid's (no spaces, special control chars) for use in file names",
    )
    parser.add_argument(
        "--filter-ext", default=None, help="filter pads by extension"
    )
    parser.add_argument(
        "--css",
        default="/styles.css",
        help="add css url to output pages, default: /styles.css",
    )
    parser.add_argument(
        "--script",
        default="/versions.js",
        help="add script url to output pages, default: /versions.js",
    )
    parser.add_argument(
        "--nopublish",
        default="__NOPUBLISH__",
        help="no publish magic word, default: __NOPUBLISH__",
    )
    parser.add_argument(
        "--publish",
        default="__PUBLISH__",
        help="the publish magic word, default: __PUBLISH__",
    )
    parser.add_argument(
        "--publish-opt-in",
        default=False,
        action="store_true",
        help="ensure `--publish` is honoured instead of `--nopublish`",
    )
    parser.add_argument(
        "--magicwords",
        default=False,
        action="store_true",
        help="download html to PADID.magicwords.html",
    )
    return parser


async def get_padids(args, info, data, session):
    if args.padid:
        padids = args.padid
    elif args.glob:
        url = info["localapiurl"] + "listAllPads?" + urlencode(data)
        padids = await agetjson(session, url)
        padids = padids["data"]["padIDs"]
        padids = [x for x in padids if fnmatch(x, args.glob)]
    else:
        url = info["localapiurl"] + "listAllPads?" + urlencode(data)
        padids = await agetjson(session, url)
        padids = padids["data"]["padIDs"]

    padids.sort()
    return padids


async def handle_pad(args, padid, data, info, session):
    global skipped, saved

    raw_ext = ".raw.txt"
    if args.no_raw_ext:
        raw_ext = ""

    data["padID"] = padid
    p = padpath(padid, args.pub, args.group, args.fix_names)
    if args.folder:
        p = os.path.join(p, padid)

    metapath = p + ".meta.json"
    revisions = None
    tries = 1
    skip = False
    padurlbase = re.sub(r"api/1.2.9/$", "p/", info["apiurl"])
    meta = {}

    while True:
        try:
            if os.path.exists(metapath):
                async with await trio.open_file(metapath) as f:
                    contents = await f.read()
                    meta.update(json.loads(contents))
                url = (
                    info["localapiurl"] + "getRevisionsCount?" + urlencode(data)
                )
                response = await agetjson(session, url)
                revisions = response["data"]["revisions"]
                if meta["revisions"] == revisions and not args.force:
                    skip = True
                    reason = "No new revisions, we already have the latest local copy"
                    break

            meta["padid"] = padid
            versions = meta["versions"] = []
            versions.append(
                {"url": padurlbase + quote(padid), "type": "pad", "code": 200,}
            )

            if revisions is None:
                url = (
                    info["localapiurl"] + "getRevisionsCount?" + urlencode(data)
                )
                response = await agetjson(session, url)
                meta["revisions"] = response["data"]["revisions"]
            else:
                meta["revisions"] = revisions

            if (meta["revisions"] == 0) and (not args.zerorevs):
                skip = True
                reason = "0 revisions, this pad was never edited"
                break

            # todo: load more metadata!
            meta["group"], meta["pad"] = splitpadname(padid)
            meta["pathbase"] = p

            url = info["localapiurl"] + "getLastEdited?" + urlencode(data)
            response = await agetjson(session, url)
            meta["lastedited_raw"] = int(response["data"]["lastEdited"])

            meta["lastedited_iso"] = datetime.fromtimestamp(
                int(meta["lastedited_raw"]) / 1000
            ).isoformat()

            url = info["localapiurl"] + "listAuthorsOfPad?" + urlencode(data)
            response = await agetjson(session, url)
            meta["author_ids"] = response["data"]["authorIDs"]

            break
        except HTTPError as e:
            tries += 1
            if tries > 3:
                print(
                    "Too many failures ({0}), skipping".format(padid),
                    file=sys.stderr,
                )
                skip = True
                reason = "PANIC, couldn't download the pad contents"
                break
            else:
                await trio.sleep(1)
        except TypeError as e:
            print(
                "Type Error loading pad {0} (phantom pad?), skipping".format(
                    padid
                ),
                file=sys.stderr,
            )
            skip = True
            reason = "PANIC, couldn't download the pad contents"
            break

    if skip:
        print("[ ] {} (skipped, reason: {})".format(padid, reason))
        skipped += 1
        return

    if args.output:
        print(padid)

    if args.all or (args.meta or args.text or args.html or args.dhtml):
        try:
            path = trio.Path(os.path.split(metapath)[0])
            if not os.path.exists(path):
                await path.mkdir()
        except OSError:
            # Note(decentral1se): the path already exists
            pass

    if args.all or args.text:
        url = info["localapiurl"] + "getText?" + urlencode(data)
        text = await agetjson(session, url)
        ver = {"type": "text"}
        versions.append(ver)
        ver["code"] = text["_code"]

        if text["_code"] == 200:
            text = text["data"]["text"]

            ##########################################
            ## ENFORCE __NOPUBLISH__ MAGIC WORD
            ##########################################
            if args.nopublish in text:
                await try_deleting(
                    (
                        p + raw_ext,
                        p + ".raw.html",
                        p + ".diff.html",
                        p + ".meta.json",
                    )
                )
                print(
                    "[ ] {} (deleted, reason: explicit __NOPUBLISH__)".format(
                        padid
                    )
                )
                skipped += 1
                return False

            ##########################################
            ## ENFORCE __PUBLISH__ MAGIC WORD
            ##########################################
            if args.publish_opt_in and args.publish not in text:
                await try_deleting(
                    (
                        p + raw_ext,
                        p + ".raw.html",
                        p + ".diff.html",
                        p + ".meta.json",
                    )
                )
                print("[ ] {} (deleted, reason: publish opt-out)".format(padid))
                skipped += 1
                return False

            ver["path"] = p + raw_ext
            ver["url"] = quote(ver["path"])
            async with await trio.open_file(ver["path"], "w") as f:
                try:
                    # Note(decentral1se): unicode handling...
                    safe_text = text.encode("utf-8", "replace").decode()
                    await f.write(safe_text)
                except Exception as exception:
                    print("PANIC: {}".format(exception))

            # once the content is settled, compute a hash
            # and link it in the metadata!

            ##########################################
            # INCLUDE __XXX__ MAGIC WORDS
            ##########################################
            if args.all or args.magicwords:
                pattern = r"__[a-zA-Z0-9]+?__"
                all_matches = re.findall(pattern, text)
                magic_words = list(set(all_matches))
                if magic_words:
                    meta["magicwords"] = magic_words

    links = []
    if args.css:
        links.append({"href": args.css, "rel": "stylesheet"})
    # todo, make this process reflect which files actually were made
    versionbaseurl = quote(padid)
    links.append(
        {
            "href": versions[0]["url"],
            "rel": "alternate",
            "type": "text/html",
            "title": "Etherpad",
        }
    )
    if args.all or args.text:
        links.append(
            {
                "href": versionbaseurl + raw_ext,
                "rel": "alternate",
                "type": "text/plain",
                "title": "Plain text",
            }
        )
    if args.all or args.html:
        links.append(
            {
                "href": versionbaseurl + ".raw.html",
                "rel": "alternate",
                "type": "text/html",
                "title": "HTML",
            }
        )
    if args.all or args.dhtml:
        links.append(
            {
                "href": versionbaseurl + ".diff.html",
                "rel": "alternate",
                "type": "text/html",
                "title": "HTML with author colors",
            }
        )
    if args.all or args.meta:
        links.append(
            {
                "href": versionbaseurl + ".meta.json",
                "rel": "alternate",
                "type": "application/json",
                "title": "Meta data",
            }
        )

    if args.all or args.dhtml:
        data["startRev"] = "0"
        url = info["localapiurl"] + "createDiffHTML?" + urlencode(data)
        dhtml = await agetjson(session, url)
        ver = {"type": "diffhtml"}
        versions.append(ver)
        ver["code"] = dhtml["_code"]
        if dhtml["_code"] == 200:
            try:
                dhtml_body = dhtml["data"]["html"]
                ver["path"] = p + ".diff.html"
                ver["url"] = quote(ver["path"])
                doc = html5lib.parse(
                    dhtml_body, treebuilder="etree", namespaceHTMLElements=False
                )
                html5tidy(
                    doc,
                    indent=True,
                    title=padid,
                    scripts=args.script,
                    links=links,
                )
                async with await trio.open_file(ver["path"], "w") as f:
                    output = ET.tostring(doc, method="html", encoding="unicode")
                    await f.write(output)
            except TypeError:
                ver["message"] = dhtml["message"]

    # Process text, html, dhtml, magicwords and all options
    downloaded_html = False
    if args.all or args.html:
        url = info["localapiurl"] + "getHTML?" + urlencode(data)
        html = await agetjson(session, url)
        ver = {"type": "html"}
        versions.append(ver)
        ver["code"] = html["_code"]
        downloaded_html = True

        if html["_code"] == 200:
            try:
                html_body = html["data"]["html"]
                ver["path"] = p + ".raw.html"
                ver["url"] = quote(ver["path"])
                doc = html5lib.parse(
                    html_body, treebuilder="etree", namespaceHTMLElements=False
                )
                html5tidy(
                    doc,
                    indent=True,
                    title=padid,
                    scripts=args.script,
                    links=links,
                )
                async with await trio.open_file(ver["path"], "w") as f:
                    output = ET.tostring(doc, method="html", encoding="unicode")
                    await f.write(output)
            except TypeError:
                ver["message"] = html["message"]

    if args.all or args.magicwords:
        if not downloaded_html:
            html = await agetjson(session, url)
        ver = {"type": "magicwords"}
        versions.append(ver)
        ver["code"] = html["_code"]

        if html["_code"] == 200:
            try:
                html_body = html["data"]["html"]
                ver["path"] = p + ".magicwords.html"
                ver["url"] = quote(ver["path"])
                for magic_word in magic_words:
                    replace_word = (
                        "<span class='highlight'>" + magic_word + "</span>"
                    )
                    if magic_word in html_body:
                        html_body = html_body.replace(magic_word, replace_word)
                doc = html5lib.parse(
                    html_body, treebuilder="etree", namespaceHTMLElements=False
                )
                html5tidy(
                    doc,
                    indent=True,
                    title=padid,
                    scripts=args.script,
                    links=links,
                )
                async with await trio.open_file(ver["path"], "w") as f:
                    output = ET.tostring(doc, method="html", encoding="unicode")
                    await f.write(output)
            except TypeError:
                ver["message"] = html["message"]

    # output meta
    if args.all or args.meta:
        ver = {"type": "meta"}
        versions.append(ver)
        ver["path"] = metapath
        ver["url"] = quote(metapath)
        async with await trio.open_file(metapath, "w") as f:
            await f.write(json.dumps(meta))

    try:
        mwords_msg = ", magic words: {}".format(", ".join(magic_words))
    except UnboundLocalError:
        mwords_msg = ""  # Note(decentral1se): for when magic_words are not counted

    print("[x] {} (saved{})".format(padid, mwords_msg))
    saved += 1
    return


async def handle_pads(args):
    global skipped, saved

    session = asks.Session(connections=args.connection)
    info = loadpadinfo(args.padinfo)
    data = {"apikey": info["apikey"]}

    padids = await get_padids(args, info, data, session)
    if args.skip:
        padids = padids[args.skip : len(padids)]

    print("=" * 79)
    print("Etherpump is warming up the engines ...")
    print("=" * 79)

    start = time.time()
    async with trio.open_nursery() as nursery:
        for padid in padids:
            nursery.start_soon(
                handle_pad, args, padid, data.copy(), info, session
            )
    end = time.time()
    timeit = round(end - start, 2)

    print("=" * 79)
    print(
        "Processed {} :: Skipped {} :: Saved {} :: Time {}s".format(
            len(padids), skipped, saved, timeit
        )
    )
    print("=" * 79)


def main(args):
    p = build_argument_parser(args)
    args = p.parse_args(args)
    trio.run(handle_pads, args)
