import socket
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import threading

# Define frame size 
FRAME_SIZE = 1024  # 1 KB per frame

# Function to handle web server requests (serving local files)
def handle_web_request(client_connection):
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
                            print(f"Received If-Modified-Since header: {if_modified_since}")
                            if_modified_since_dt = parsedate_to_datetime(if_modified_since)
                            print(f"Parsed If-Modified-Since date: {if_modified_since_dt}")

                            if if_modified_since_dt is None:
                                print("Failed to parse the If-Modified-Since header correctly.")
                                client_connection.sendall(generate_response(400).encode('utf-8'))
                                return

                            file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path), timezone.utc)
                            print(f"File modification time: {file_modified_time}")

                            if file_modified_time <= if_modified_since_dt:
                                print("File not modified since the provided date.")
                                client_connection.sendall(generate_response(304).encode('utf-8'))
                                return
                        except (TypeError, ValueError) as e:
                            print(f"Error parsing If-Modified-Since header: {e}")
                            client_connection.sendall(generate_response(400).encode('utf-8'))
                            return

                    # Serve file in frames
                    with open(file_path, 'rb') as file:
                        while True:
                            content = file.read(FRAME_SIZE)
                            if not content:
                                break
                            client_connection.sendall(generate_response(200, content).encode('utf-8'))
                    return

                else:
                    client_connection.sendall(generate_response(404).encode('utf-8'))
                    return

    finally:
        client_connection.close()

# Function to forward the request to an origin server (for proxy server behavior)
def handle_proxy_request(client_connection, request):
    try:
        origin_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        origin_server.connect(('example.com', 80)) 
        origin_server.sendall(request)

        while True:
            response = origin_server.recv(4096)
            if len(response) == 0:
                break

            client_connection.sendall(response)

    finally:
        origin_server.close()
        client_connection.close()

# Function to handle requests (web server or proxy)
def handle_request(client_connection, client_address):
    try:
        # Receive the request and check if it's meant for the proxy or the web server
        request = client_connection.recv(1024)
        request_str = request.decode('utf-8')
        print(f"New request from {client_address}: {request_str.splitlines()[0]}")

        # Check if the request is for the proxy server (e.g., trying to access external websites)
        if "example.com" in request_str:  # Proxy server functionality
            print(f"Proxying request for external server from {client_address}")
            handle_proxy_request(client_connection, request)
        else:
            # Else, treat it as a request to the web server (local files)
            print(f"Handling local web request from {client_address}")
            handle_web_request(client_connection)
    except Exception as e:
        print(f"Error handling request from {client_address}: {e}")
    finally:
        client_connection.close()

# Function to generate responses based on status codes
def generate_response(status_code, content=None):
    if status_code == 200:
        response_line = "HTTP/1.1 200 OK\r\n"
        headers = "Content-Type: text/html\r\n\r\n"
        return response_line + headers + content.decode('utf-8') if content else response_line + headers
    
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
server_socket.listen(10)
print("Combined Web/Proxy server with HOL blocking mitigation is running on http://localhost:8080")

# Multithreading: handle multiple clients concurrently
def start_server():
    while True:
        client_connection, client_address = server_socket.accept()
        print(f"New connection from {client_address}")

        # Create a new thread for each client connection
        client_thread = threading.Thread(target=handle_request, args=(client_connection, client_address))
        client_thread.start()

# Start the combined server
start_server()
