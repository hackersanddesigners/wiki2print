"""API for programming against pads marked with __MAGIC_WORDS__."""

__all__ = ['magicword']

import json
from pathlib import Path

from etherpump.api._utils import ensure_init, get_pad_ids
from etherpump.commands.pull import main as pull


def magicword(word):
    """Decorator for handling magic words."""

    ensure_init()
    pull(['--all', '--publish-opt-in', '--publish', word])

    pads = {}
    for pad_id in get_pad_ids():
        pads[pad_id] = {}
        try:
            pads[pad_id]['html'] = open(Path(f'./p/{pad_id}.raw.html')).read()
            pads[pad_id]['txt'] = open(Path(f'./p/{pad_id}.raw.txt')).read()
            pads[pad_id]['meta'] = json.loads(
                open(Path(f'./p/{pad_id}.meta.json')).read()
            )
            pads[pad_id]['dhtml'] = open(Path(f'./p/{pad_id}.raw.dhtml')).read()
        except FileNotFoundError:
            pass

    def wrap(userfunc):
        def wrappedf(*args):
            userfunc(pads)

        return wrappedf

    return wrap
