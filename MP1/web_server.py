import socket
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import threading

# Function to handle request validation and response generation
def handle_request(client_connection):
    try:
        # Receive the request from the client
        request = client_connection.recv(1024).decode('utf-8')
        print(f"Raw request: {request}")

        request_lines = request.splitlines()
        
        if len(request_lines) > 0:
            try:
                method, path, version = request_lines[0].split()
            except ValueError:
                client_connection.sendall(generate_response(400).encode('utf-8'))
                return

            if path == '/':
                path = '/test.html'  # Serve test.html by default

            if method not in ['GET']:
                client_connection.sendall(generate_response(501).encode('utf-8'))
                return

            if version != "HTTP/1.1":
                client_connection.sendall(generate_response(400).encode('utf-8'))
                return

            headers = {}
            for line in request_lines[1:]:
                if ":" in line:
                    key, value = line.split(":", 1)  # Split only on the first colon
                    headers[key.strip()] = value.strip()

            if "Host" not in headers:
                client_connection.sendall(generate_response(400).encode('utf-8'))
                return

            if method == 'GET':
                if_modified_since = headers.get("If-Modified-Since", None)
                file_path = '.' + path

                if os.path.isfile(file_path):
                    if if_modified_since:
                        try:
                            # Debugging: Log the If-Modified-Since header
                            print(f"Received If-Modified-Since header: {if_modified_since}")

                            # Parse the If-Modified-Since header
                            if_modified_since_dt = parsedate_to_datetime(if_modified_since)

                            if if_modified_since_dt is None:
                                print("Failed to parse the If-Modified-Since header correctly.")
                                client_connection.sendall(generate_response(400).encode('utf-8'))
                                return

                            # Get the file's modification time
                            file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path), timezone.utc)
                            print(f"File modification time: {file_modified_time}")

                            # Compare file modification time with If-Modified-Since header
                            if file_modified_time <= if_modified_since_dt:
                                client_connection.sendall(generate_response(304).encode('utf-8'))
                                return
                        except (TypeError, ValueError) as e:
                            print(f"Error parsing If-Modified-Since header: {e}")
                            client_connection.sendall(generate_response(400).encode('utf-8'))
                            return

                    # Return 200 OK with file content
                    with open(file_path, 'rb') as file:
                        content = file.read()
                    client_connection.sendall(generate_response(200, content).encode('utf-8'))
                    return

                else:
                    client_connection.sendall(generate_response(404).encode('utf-8'))
                    return

    finally:
        client_connection.close()

# Function to generate responses based on status codes
def generate_response(status_code, content=None):
    if status_code == 200:
        response_line = "HTTP/1.1 200 OK\r\n"
        headers = "Content-Type: text/html\r\n\r\n"
        return response_line + headers + content.decode('utf-8')
    
    elif status_code == 304:
        return "HTTP/1.1 304 Not Modified\r\n\r\n"

    elif status_code == 400:
        return "HTTP/1.1 400 Bad Request\r\n\r\n<h1>400 Bad Request</h1>"
    
    elif status_code == 404:
        return "HTTP/1.1 404 Not Found\r\n\r\n<h1>404 Not Found</h1>"

    elif status_code == 501:
        return "HTTP/1.1 501 Not Implemented\r\n\r\n<h1>501 Not Implemented</h1>"

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_socket.bind(('0.0.0.0', 8080))  # Binds to all available interfaces

# Listen for incoming connections
server_socket.listen(5)
print("Server is running on http://localhost:8080")

# Handle multiple client connections using threads
def start_server():
    while True:
        client_connection, client_address = server_socket.accept()
        print(f"New connection from {client_address}")

        # Create a new thread for each client connection
        client_thread = threading.Thread(target=handle_request, args=(client_connection,))
        client_thread.start()

# Start the server
start_server()
