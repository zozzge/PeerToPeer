import os
import json
import requests
import time
from requests.exceptions import RequestException

# Chunks directory
if not os.path.exists('chunks'):
    os.makedirs('chunks')

# Create a file for the download log
with open('download_log.txt', 'a') as log_file:
    log_file.write('Download Log\n')
    log_file.write('====================\n')

while True:  # Make the Chunk Downloader service persistent
    # Read content dictionary
    with open('content_dictionary.json', 'r') as file:
        content = file.read()
        if content:
            content_dict = json.loads(content)
        else:
            content_dict = {}

    # Get the name of the content to be downloaded from the user
    content_name = input("Enter the name of the content you want to download: ")

    # Maximum retries for each IP
    MAX_RETRIES = 3

    # Retrieve chunk names dynamically from content dictionary
    chunknames = [name for name in content_dict if name.startswith(content_name)]

    # Create a list to hold the status of each chunk
    downloaded_chunks = []

    # Download each chunk
    for chunk_name in chunknames:
        if chunk_name in content_dict:
            for ip in content_dict[chunk_name]:
                for _ in range(MAX_RETRIES):
                    try:
                        # Prepare the JSON payload
                        payload = {"requested_content": chunk_name}
                        headers = {"Content-Type": "application/json"}

                        response = requests.post(f'http://{ip}:5002/', json=payload, headers=headers, timeout=5)

                        if response.status_code == 200:
                            with open(f'chunks/{chunk_name}', 'wb') as file:
                                file.write(response.content)
                            downloaded_chunks.append(chunk_name)  # add this chunk to downloaded list

                            # Log creation
                            with open('download_log.txt', 'a') as log_file:
                                log_file.write(f'{time.ctime()} - Downloaded {chunk_name} from {ip}\n')

                            response.close()  # Close the TCP session
                            break
                    except RequestException:
                        continue
                else:
                    print(f"Unable to connect to {ip} for {chunk_name}. Moving to next IP.")
            else:
                print(f"CHUNK {chunk_name} CANNOT BE DOWNLOADED FROM ONLINE PEERS.")
        else:
            print(f"CHUNK {chunk_name} IS NOT AVAILABLE.")

    # Check if all chunks have been downloaded
    if len(downloaded_chunks) == len(chunknames):
        print("All chunks have been successfully downloaded.")
        # Merging operation
        content_name = content_name.split(".")[0]  # Remove the file extension
        with open(content_name + '.png', 'wb') as outfile:
            for chunk in chunknames:
                try:
                    with open('chunks/' + chunk, 'rb') as infile:
                        outfile.write(infile.read())
                except FileNotFoundError:  # Chunk could not be downloaded or is not available
                    print(f"CHUNK {chunk} IS MISSING. Unable to complete content assembly.")
                    break
            else:  # All chunks have been successfully merged
                print(f"Content {content_name} has been successfully downloaded and assembled.")
    else:
        print("Some chunks could not be downloaded.")