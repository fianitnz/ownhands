# -*- coding: utf-8 -*-
from nose.tools import eq_

from serve import HTTPServer, parse_http, encode_http

class MockConnection(object):
    def __init__(self, data=''):
        """Создаём буферы для приёма и передачи"""
        self.read = data
        self.sent = ''

    def recv(self, buf_size=None):
        """HTTP читает всё сразу, поэтому на буфер пофиг"""
        return self.read

    def send(self, data):
        """Просто накапливаем отправленое"""
        self.sent += data

    def close(self):
        """Закрывать нечего, просто заглушка"""
        pass

class MockClient(object):
    def __init__(self, server):
        self.server = server

    def __call__(self, url, method="GET", body='', **headers):
        conn = MockConnection(encode_http((method, url, "HTTP/1.0"), body, **headers))
        self.server.on_connect(conn, None)
        return parse_http(conn.sent)

class TestHTTP(object):
    def test_request(self):
        eq_(encode_http(('GET', '/', 'HTTP/1.0'), user_agent="test/shmest"),
            'GET / HTTP/1.0\r\nUser-Agent: test/shmest\r\n')

        eq_(encode_http(('POST', '/', 'HTTP/1.0'), 'post=body', user_agent="test/shmest"),
            'POST / HTTP/1.0\r\nUser-Agent: test/shmest\r\n\r\npost=body')

        eq_(parse_http('POST / HTTP/1.0\r\nUser-Agent: test/shmest\r\n\r\npost=body'),
            (['POST', '/', 'HTTP/1.0'], {'USER-AGENT': 'test/shmest'}, 'post=body'))

    def test_response(self):
        data = 'HTTP/1.0 200 OK\r\nSpam: eggs\r\nTest-Me: please\r\n\r\nHellow, orld!\n'

        eq_(data, encode_http(('HTTP/1.0', '200', 'OK'), 'Hellow, orld!\n', test_me='please', spam="eggs"))
        
        reply, headers, body = parse_http(data)
        eq_(reply, ['HTTP/1.0', '200', 'OK'])
        eq_(headers, {'TEST-ME': 'please', 'SPAM': 'eggs'})
        eq_(body, 'Hellow, orld!\n')

class TestServer(object):
    def test_serve(self):
        server = HTTPServer()
        client = MockClient(server)

        reply, headers, body = client('/hellow/orld/')
        eq_(reply, ['HTTP/1.0', '200', 'OK'])
        eq_(headers['SERVER'], 'OwnHands/0.1')
        eq_(body, 'Hi there!\n')

