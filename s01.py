# -*- coding: utf-8 -*-
import socket

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # параметры для создания TCP-сокета
socket.bind(('', 8000))  # слушать на всех адресах, на порту 8000. Чтобы создать сервер на порту ниже 8000 нужен рут, но это не труъ.
socket.listen(1)  # перевести сокет в режим ожидания входящих соединений

while True:
    conn, addr = socket.accept()  # ожидать установки соединения

    data = conn.recv(1024).split('\r\n')  # считываем запрос и бьём на строки
    method, url, proto = data[0].split(' ', 2)  # обрабатываем первую строку

    headers = {}
    for pos, line in enumerate(data[1:]):  # проходим по строкам и заодно запоминаем позицию
        if not line.strip():  # пустая строка = конец заголовков, начало тела
	    break
        print pos, repr(line)
        key, value = line.split(': ', 1)  # разбираем строку с заголовком
        headers[key.upper()] = value  # приводим ключ к "нормальному" виду чтобы обращение было регистронезависимым

    # всё остальное - тело запроса
    body = '\r\n'.join(data[pos+2:])

    print method, url, repr(body)

    conn.send("HTTP/1.0 200 OK\r\n")  # мы не умеем никаких фишечек версии 1.1, поэтому будем сразу честны
    conn.send("Server: OwnHands/0.1\r\n")  # Поехали заголовки...
    conn.send("Content-Type: text/plain\r\n")  # разметка нам тут пока не нужна, поэтому говорим клиенту показывать всё как есть
    conn.send("\r\n")  # Кончились заголовки, всё остальное - тело ответа
    conn.send("Hi there!")  # привет мир
    conn.close()  # сбрасываем буфера, закрываем соединение
