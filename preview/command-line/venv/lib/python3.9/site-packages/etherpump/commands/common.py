import json
import os
import re
import sys
from html.entities import name2codepoint
from time import sleep
from urllib.parse import quote_plus, unquote_plus
from urllib.request import HTTPError, urlopen

import trio

groupnamepat = re.compile(r"^g\.(\w+)\$")


def splitpadname(padid):
    m = groupnamepat.match(padid)
    if m:
        return (m.group(1), padid[m.end() :])
    else:
        return ("", padid)


def padurl(padid,):
    return padid


def padpath(padid, pub_path="", group_path="", normalize=False):
    g, p = splitpadname(padid)
    p = quote_plus(p)
    if normalize:
        p = p.replace(" ", "_")
        p = p.replace("(", "")
        p = p.replace(")", "")
        p = p.replace("?", "")
        p = p.replace("'", "")
    if g:
        return os.path.join(group_path, g, p)
    else:
        return os.path.join(pub_path, p)


def padpath2id(path):
    dd, p = os.path.split(path)
    gname = dd.split("/")[-1]
    p = unquote_plus(p)
    if gname:
        return "{0}${1}".format(gname, p).decode("utf-8")
    else:
        return p.decode("utf-8")


def getjson(url, max_retry=3, retry_sleep_time=3):
    ret = {}
    ret["_retries"] = 0
    while ret["_retries"] <= max_retry:
        try:
            f = urlopen(url)
            data = f.read()
            data = data.decode("utf-8")
            rurl = f.geturl()
            f.close()
            ret.update(json.loads(data))
            ret["_code"] = f.getcode()
            if rurl != url:
                ret["_url"] = rurl
            return ret
        except ValueError as e:
            url = "http://localhost" + url
        except HTTPError as e:
            print("HTTPError {0}".format(e), file=sys.stderr)
            ret["_code"] = e.code
            ret["_retries"] += 1
            if retry_sleep_time:
                sleep(retry_sleep_time)
    return ret


async def agetjson(session, url):
    """The asynchronous version of getjson."""
    RETRY = 20
    TIMEOUT = 10

    ret = {}
    ret["_retries"] = 0

    try:
        response = await session.get(url, timeout=TIMEOUT, retries=RETRY)
        rurl = response.url
        ret.update(response.json())
        ret["_code"] = response.status_code
        if rurl != url:
            ret["_url"] = rurl
        return ret
    except Exception as e:
        print("Failed to download {}, saw {}".format(url, str(e)))
        return


def loadpadinfo(p):
    with open(p) as f:
        info = json.load(f)
        if "localapiurl" not in info:
            info["localapiurl"] = info.get("apiurl")
    return info


# Python developer Fredrik Lundh (author of elementtree, among other things)
# has such a function on his website, which works with decimal, hex and named
# entities:

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return chr(int(text[3:-1], 16))
                else:
                    return chr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = chr(name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is

    return re.sub("&#?\w+;", fixup, text)


def istty():
    return sys.stdout.isatty() and os.environ.get("TERM") != "dumb"


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]
