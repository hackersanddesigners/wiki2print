"""Utilities for API functions."""

from pathlib import Path
from urllib.parse import urlencode

from etherpump.commands.common import getjson, loadpadinfo
from etherpump.commands.init import main


def ensure_init():
    """Ensure etherpump has already been init'd."""
    try:
        main([])
    except SystemExit:
        pass


def get_pad_ids():
    """Retrieve all available pad ids."""
    info = loadpadinfo(Path('.etherpump/settings.json'))
    data = {'apikey': info['apikey']}
    url = info['localapiurl'] + 'listAllPads?' + urlencode(data)
    return getjson(url)['data']['padIDs']
