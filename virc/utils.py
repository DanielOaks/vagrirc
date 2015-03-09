#!/usr/bin/env python3
# VagrIRC Virc library

def get_members(zip):
    """get_members for zipfile, stripping common directory prefixes.

    Taken from http://stackoverflow.com/questions/8689938
    """
    parts = []
    for name in zip.namelist():
        if not name.endswith('/'):
            parts.append(name.split('/')[:-1])
    prefix = os.path.commonprefix(parts) or ''
    if prefix:
        prefix = '/'.join(prefix) + '/'
    offset = len(prefix)
    for zipinfo in zip.infolist():
        name = zipinfo.filename
        if len(name) > offset:
            zipinfo.filename = name[offset:]
            yield zipinfo
