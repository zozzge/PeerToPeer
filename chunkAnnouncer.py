import os
import time
import json
import math
import socket

filename = input("Please enter the filename with extension (e.g., 'my_file.png'): ")
announce_path = "./announce1/"

if not os.path.exists(announce_path):
    os.makedirs(announce_path)

content_name, file_extension = os.path.splitext(filename)
file_path = input("Enter the file path of the content you want to announce: ")
if not file_path.endswith('/'):
    file_path += '/'
c = os.path.getsize(file_path + filename)
CHUNK_SIZE = math.ceil(c / 5)

print(c)
index = 1
with open(file_path + filename, 'rb') as infile:
    while True:
        chunk = infile.read(CHUNK_SIZE)
        if not chunk:
            break
        chunkname = content_name + '_' + str(index) + file_extension
        with open(announce_path + chunkname, 'wb+') as chunk_file:
            chunk_file.write(chunk)
        index += 1

print("Split into", index - 1, "chunks. Starting to announce these files...")

# Getting file names without extensions
chunks = [os.path.splitext(f)[0] for f in os.listdir(announce_path) if os.path.isfile(os.path.join(announce_path, f))]

BROADCAST_TO_IP = input("Please enter your broadcast IP: ")
BROADCAST_PORT = 5002
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

while True:
    data = {"chunks": chunks}
    s.sendto(bytes(json.dumps(data), "utf-8"), (BROADCAST_TO_IP, BROADCAST_PORT))
    print("Message sent!")
    time.sleep(5)