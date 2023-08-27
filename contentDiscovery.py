import socket
import json
from collections import defaultdict

UDP_IP = "0.0.0.0"
UDP_PORT = 5001

content_dict = defaultdict(list)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:
    print("Listening for messages...")
    data, addr = sock.recvfrom(1024)

    try:
        message = json.loads(data)

        for chunk_name in message.get('chunks', []):
            content_dict[chunk_name].append(addr[0])

        print(f'{addr[0]}: {", ".join(message.get("chunks", []))}')

    except json.JSONDecodeError as e:
        print(f"Received a message that's not in JSON format: {e}")

    with open('content_dictionary.json', 'w') as file:
        file.write(json.dumps(content_dict))
    print("Updated content dictionary.")