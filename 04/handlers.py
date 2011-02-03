# -*- coding: utf-8 -*-

def serve_static(request):
    try:
        data = open(request.url[1:]).read()
    except IOError as err:
        if err.errno == 2:
            return request.reply('404', 'Not found', '%s: not found' % request.url)
        if err.errno == 13:
            return request.reply('403', 'Permission denied', '%s: permission denied' % request.url)
        if err.errno == 21:
            return request.reply('403', 'Directory listing denied', '%s: directory listing denied' % request.url)
        raise
    request.reply(body=data, content_length=len(data))

