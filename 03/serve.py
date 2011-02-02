# -*- coding: utf-8 -*-
import socket
from datetime import datetime

def parse_http(data):
    lines = data.split('\r\n')
    query = lines[0].split(' ', 2)

    headers = {}
    for pos, line in enumerate(lines[1:]):
        if not line.strip():
            break
        key, value = line.split(': ', 1)
        headers[key.upper()] = value

    body = '\r\n'.join(lines[pos+2:])

    return query, headers, body


def encode_http(query, body='', **headers):
    data = [" ".join(query)]

    headers = "\r\n".join("%s: %s" %
        ("-".join(part.title() for part in key.split('_')), value)
        for key, value in sorted(headers.iteritems()))

    if headers:
        data.append(headers)

    data.append('')

    if body:
        data.append(body)

    return "\r\n".join(data)

class Request(object):
    """Контейнер с данными текущего запроса и средством ответа на него"""

    def __init__(self, method, url, headers, body, conn):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body
        self.conn = conn

    def __str__(self):
        return "%s %s %r" % (self.method, self.url, self.headers)

    def reply(self, code='200', status='OK', body='', **headers):
        headers.setdefault('server', 'OwnHands/0.1')
        headers.setdefault('content_type', 'text/plain')
        headers.setdefault('content_length', len(body))
        headers.setdefault('connection', 'close')
        headers.setdefault('date', datetime.now().ctime())

        self.conn.send(encode_http(('HTTP/1.0', code, status), body, **headers))
        self.conn.close()

class HTTPServer(object):
    def __init__(self, host='', port=8000):
        """Распихиваем по карманам аргументы для старта"""
        self.host = host
        self.port = port
        self.handlers = []

    def serve(self):
        """Цикл ожидания входящих соединений"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 8000))
        sock.listen(50)
        
        while True:
            conn, addr = sock.accept()
            self.on_connect(conn, addr)

    def on_connect(self, conn, addr):
        """Соединение установлено, вычитываем запрос"""
        (method, url, proto), headers, body = parse_http(conn.recv(1024))
        self.on_request(Request(method, url, headers, body, conn))

    def on_request(self, request):
        """Обработка запроса"""
        print request

        for pattern, handler in self.handlers:
            if pattern(request):
                handler(request)
                return True

        # никто не взялся ответить
        request.reply('404', 'Not found', 'Письмо самурай получил\nТают следы на песке\nСтраница не найдена')

    def register(self, pattern, handler):
        self.handlers.append((pattern, handler))

if __name__ == '__main__':
    server = HTTPServer()
    server.serve()

