import os
import socket
import time
import json
from threading import Thread

# Create announce directory, if it does not exist
if not os.path.exists('announce'):
    os.makedirs('announce')

# Create log file
with open('upload_log.txt', 'w') as log_file:
    log_file.write('Upload Log\n')
    log_file.write('====================\n')

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))  # connecting to a random IP address
        ip = s.getsockname()[0]
    except Exception as e:
        print(e)
        ip = '127.0.0.1'
    finally:
        s.close()
        return ip

def handle_client(client_socket, client_address):
    request = client_socket.recv(1024)
    if request:
        try:
            request_json = json.loads(request.decode()) # Parse the incoming JSON request
            chunk_name = request_json.get('requested_content')
            if chunk_name:
                with open(f'announce/{chunk_name}', 'rb') as file:
                    data = file.read(1024)
                    while data:
                        client_socket.send(data)
                        data = file.read(1024)

                # Log creation
                with open('upload_log.txt', 'a') as log_file:
                    log_file.write(f'Sent {chunk_name} to {client_address[0]} at {time.ctime()}\n')
            else:
                print(f"Invalid JSON data in request: {request_json}")
        except FileNotFoundError:
            print(f"File {chunk_name} not found.")
        except json.JSONDecodeError:
            print(f"Invalid request: {request}")
    client_socket.close()

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((get_local_ip(), 5002))
    server_socket.listen(1)

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
        client_thread = Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

# Start server in a thread
server_thread = Thread(target=run_server)
server_thread.start()

while True:
    time.sleep(1)  # Keep server running indefinitely