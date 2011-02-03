def serve_static(request):
    try:
        data = open(request.url[1:]).read()
    except IOError as err:
        if err.errno == 2:
            return request.reply('404', '%s not found' % request.url)
        raise
    request.reply(body=data, content_length=len(data))

