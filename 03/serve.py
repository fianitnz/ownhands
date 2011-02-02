# -*- coding: utf-8 -*-
import socket

class HTTPServer(object):
    def __init__(self, host='', port=8000):
        """Распихиваем по карманам аргументы для старта"""
        self.host = host
        self.port = port

    def serve(self):
        """Цикл ожидания входящих соединений"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 8000))
        sock.listen(50)  # количество соединений в очереди, перед тем, как ОС откажется их принимать
        
        while True:
            conn, addr = sock.accept()
            self.on_connect(conn, addr)

    def on_connect(self, conn, addr):
        """Соединение установлено, вычитываем запрос"""
        data = conn.recv(1024).split('\r\n')
        method, url, proto = data[0].split(' ', 2)

        headers = {}
        for pos, line in enumerate(data[1:]):
            if not line.strip():
                break
            key, value = line.split(': ', 1)
            headers[key.upper()] = value

        body = '\r\n'.join(data[pos+2:])
        self.on_request(method, url, headers, body, conn)

    def on_request(self, method, url, headers, body, conn):
        """Обработка запроса"""
        print method, url, repr(body)

        conn.send("HTTP/1.0 200 OK\r\n")
        conn.send("Server: OwnHands/0.1\r\n")
        conn.send("Content-Type: text/plain\r\n")
        conn.send("\r\n")
        conn.send("Hi there!\n")
        conn.close()

if __name__ == '__main__':
    server = HTTPServer()
    server.serve()

