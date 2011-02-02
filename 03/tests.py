# -*- coding: utf-8 -*-
from nose.tools import eq_

from serve import HTTPServer

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
        # Первая строка - запрос
        request = "%s %s HTTP/1.0" % (method, url)

        # Дефолтные заголовки 
        headers.setdefault('host', 'localhost')
        headers.setdefault('user_agent', 'MockClient/0.1')
        headers.setdefault('connection', 'close')

        # Приводим заголовки к красивому Http-Виду
        headers = "\r\n".join("%s: %s" %
            ("-".join(part.title() for part in key.split('_')), value)
            for key, value in sorted(headers.iteritems()))
        
        # Собираем всё в кучу^W HTTP-запрос
        data = "\r\n".join((request, headers, ''))
        data += body

        # Заворачиваем в соединение и пускаем в обработку
        return self.server.on_connect(MockConnection(data), None)

class TestHttp(object):
    def test_serve(self):
        server = HTTPServer()
        client = MockClient(server)
        client('/hellow/orld/')

