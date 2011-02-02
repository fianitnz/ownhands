# -*- coding: utf-8 -*-
import socket

def parse_http(data):
    lines = data.split('\r\n')
    query = lines[0].split(' ')

    headers = {}
    for pos, line in enumerate(lines[1:]):
        if not line.strip():
            break
        key, value = line.split(': ', 1)
        headers[key.upper()] = value

    body = '\r\n'.join(lines[pos+2:])

    return query, headers, body


def encode_http(query, body='', **headers):
    request = " ".join(query)

    headers = "\r\n".join("%s: %s" %
        ("-".join(part.title() for part in key.split('_')), value)
        for key, value in sorted(headers.iteritems()))
    
    return "\r\n".join((request, headers, '', body) if body else (request, headers, ''))


class HTTPServer(object):
    def __init__(self, host='', port=8000):
        """Распихиваем по карманам аргументы для старта"""
        self.host = host
        self.port = port

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
        self.on_request(method, url, headers, body, conn)

    def on_request(self, method, url, headers, body, conn):
        """Обработка запроса"""
        print method, url, repr(body)
        conn.send(encode_http(("HTTP/1.0", "200", "OK"), "Hi there!\n", server="OwnHands/0.1"))
        conn.close()

if __name__ == '__main__':
    server = HTTPServer()
    server.serve()

