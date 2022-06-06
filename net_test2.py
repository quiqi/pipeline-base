import socket

import threading
import struct
import json
import asyncio

phone = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
phone.connect(('127.0.0.1', 8083))

phone.send('hello'.encode('utf-8'))
len_head = struct.unpack('i', phone.recv(4))[0]
print(len_head)
b_head = phone.recv(len_head)
head = json.loads(b_head.decode('utf-8'))
print(head)


phone.close()

