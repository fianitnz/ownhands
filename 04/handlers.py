# -*- coding: utf-8 -*-

import os, time
from os.path import relpath

from serve import HTTPError

def serve_static(url, root):
    cut = len(url)

    DATE_RFC1123 = '%a, %d %b %Y %H:%I:%S GMT'

    def pattern(request):
        return request.url.startswith(url)

    def handler(request):
        path = "%s/%s" % (root, request.url[cut:])

        if relpath(path).startswith('..'):
            raise HTTPError(404)

        try:
            stat = os.stat(path)
            if 'IF-MODIFIED-SINCE' in request.headers:
                try:
                    request_mtime = time.mktime(time.strptime(request.headers['IF-MODIFIED-SINCE'], DATE_RFC1123))
                except ValueError:
                    request_mtime = None                             # в заголовках мусор
                if request_mtime and request_mtime < stat.st_mtime:
                    return request.reply('304', 'Not modified', '')

            mod_time = time.strftime(DATE_RFC1123, time.gmtime(stat.st_mtime))
            data = open(path).read()
        except (OSError, IOError) as err:
            if err.errno == 2:
                raise HTTPError(404)  # not found
            if err.errno == 13:
                raise HTTPError(403)  # no access
            if err.errno == 21:
                raise HTTPError(403)  # is a directory
            raise

        request.reply(body=data, content_length=stat.st_size, last_modified=mod_time)

    return pattern, handler

