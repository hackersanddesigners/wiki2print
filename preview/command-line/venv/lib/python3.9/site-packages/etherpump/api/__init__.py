from functools import wraps
from os.path import exists
from pathlib import Path
from urllib.parse import urlencode

from etherpump.commands.common import getjson, loadpadinfo
from etherpump.commands.creatediffhtml import main as creatediffhtml  # noqa
from etherpump.commands.deletepad import main as deletepad  # noqa
from etherpump.commands.dumpcsv import main as dumpcsv  # noqa
from etherpump.commands.gethtml import main as gethtml  # noqa
from etherpump.commands.gettext import main as gettext  # noqa
from etherpump.commands.index import main as index  # noqa
from etherpump.commands.init import main  # noqa
from etherpump.commands.init import main as init
from etherpump.commands.list import main as list  # noqa
from etherpump.commands.listauthors import main as listauthors  # noqa
from etherpump.commands.publication import main as publication  # noqa
from etherpump.commands.pull import main as pull
from etherpump.commands.revisionscount import main as revisionscount  # noqa
from etherpump.commands.sethtml import main as sethtml  # noqa
from etherpump.commands.settext import main as settext  # noqa
from etherpump.commands.showmeta import main as showmeta  # noqa


def ensure_init():
    path = Path(".etherpump/settings.json").absolute()
    if not exists(path):
        try:
            main([])
        except SystemExit:
            pass


def get_pad_ids():
    info = loadpadinfo(Path(".etherpump/settings.json"))
    data = {"apikey": info["apikey"]}
    url = info["localapiurl"] + "listAllPads?" + urlencode(data)
    return getjson(url)["data"]["padIDs"]


def magic_word(word, fresh=True):
    ensure_init()

    if fresh:
        pull(["--text", "--meta", "--publish-opt-in", "--publish", word])

    pads = {}
    pad_ids = get_pad_ids()
    for pad_id in pad_ids:
        path = Path("./p/{}.raw.txt".format(pad_id)).absolute()
        try:
            with open(path, "r") as handle:
                text = handle.read()
            if word in text:
                pads[pad_id] = {}
                pads[pad_id]["txt"] = text
        except FileNotFoundError:
            continue

    def _magic_word(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(pads)

        return wrapper

    return _magic_word
