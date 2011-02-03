# -*- coding: utf-8 -*-
from nose.tools import eq_

from serve import HTTPServer, parse_http, encode_http
from handlers import serve_static

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
        """Тестирование в режиме запроса: клиент сериализует, сервер разбирает"""

        eq_(encode_http(('GET', '/', 'HTTP/1.0'), user_agent="test/shmest"),
            'GET / HTTP/1.0\r\nUser-Agent: test/shmest\r\n')

        eq_(encode_http(('POST', '/', 'HTTP/1.0'), 'post=body', user_agent="test/shmest"),
            'POST / HTTP/1.0\r\nUser-Agent: test/shmest\r\n\r\npost=body')

        eq_(parse_http('POST / HTTP/1.0\r\nUser-Agent: test/shmest\r\n\r\npost=body'),
            (['POST', '/', 'HTTP/1.0'], {'USER-AGENT': 'test/shmest'}, 'post=body'))

    def test_response(self):
        """Тестирование в режиме ответа: сервер сериализует, клиент разбирает"""
        data = 'HTTP/1.0 200 OK\r\nSpam: eggs\r\nTest-Me: please\r\n\r\nHellow, orld!\n'

        eq_(data, encode_http(('HTTP/1.0', '200', 'OK'), 'Hellow, orld!\n', test_me='please', spam="eggs"))

        reply, headers, body = parse_http(data)
        eq_(reply, ['HTTP/1.0', '200', 'OK'])
        eq_(headers, {'TEST-ME': 'please', 'SPAM': 'eggs'})
        eq_(body, 'Hellow, orld!\n')

class TestServer(object):
    def setup(self):
        self.server = HTTPServer()
        self.client = MockClient(self.server)

    def test_404(self):
        reply, headers, body = self.client('/you/cant/find/me/?yet')
        eq_(reply, ['HTTP/1.0', '404', 'Not found'])
        eq_(headers['SERVER'], 'OwnHands/0.1')

    def test_handlers(self):
        self.server.register(lambda r: r.url.startswith('/hello/'),
                             lambda r: r.reply(body='hi'))

        reply, headers, body = self.client('/hello/world/')
        eq_(reply[1], '200')
        eq_(body, 'hi')

        self.server.register(lambda r: r.method == 'POST',
                             lambda r: r.reply(body=r.body))
        reply, headers, body = self.client('/looking/for/a/POST/', 'POST', 'any url')
        eq_(reply[1], '200')
        eq_(body, 'any url')

        self.server.register(lambda r: r.url == '/crash/me/', lambda r: no_you)
        request, headers, body = self.client('/crash/me/')
        eq_(request[1], '500')
        assert 'NameError' in body, body


class TestHandlers(object):
    def setup(self):
        self.server = HTTPServer()
        self.client = MockClient(self.server)

    def test_static(self):
        """Раздача файлов с диска"""

        self.server.register(*serve_static('/', '.')) # обслуживать все запросы как файл-сервер

        eq_('404', self.client('/give-me-nice-404')[0][1])

        reply, headers, body = self.client('/handlers.py') # файл из каталога сервера
        eq_('200', reply[1])
        data = open('handlers.py').read()
        eq_(body, data)
        eq_(int(headers['CONTENT-LENGTH']), len(data))

        eq_('404', self.client('/../../../../../../../../../../../etc/passwd')[0][1])

