# -*- coding: utf-8 -*-

from os.path import relpath

from serve import HTTPError

def serve_static(request):
    path = request.url[1:]
    if relpath(path).startswith('..'):
        raise HTTPError(404)

    try:
        data = open(path).read()
    except IOError as err:
        if err.errno == 2:
            raise HTTPError(404)  # not found
        if err.errno == 13:
            raise HTTPError(403)  # no access
        if err.errno == 21:
            raise HTTPError(403)  # is a directory
        raise

    request.reply(body=data, content_length=len(data))

