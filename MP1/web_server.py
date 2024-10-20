import socket
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_socket.bind(('localhost', 8080))

# Listen for incoming connections
server_socket.listen(5)
print("Server is running on http://localhost:8080")

# Function to handle request validation and response generation
def handle_request(request):
    request_lines = request.splitlines()
    
    if len(request_lines) > 0:
        try:
            method, path, version = request_lines[0].split()
        except ValueError:
            return generate_response(400)

        if path == '/':
            path = '/index.html'

        if method not in ['GET']:
            return generate_response(501)

        if version != "HTTP/1.1":
            return generate_response(400)

        headers = {line.split(":")[0].strip(): line.split(":")[1].strip() for line in request_lines[1:] if ":" in line}
        if "Host" not in headers:
            return generate_response(400)

        if method == 'GET':
            if_modified_since = headers.get("If-Modified-Since", None)
            file_path = '.' + path

            if os.path.isfile(file_path):
                if if_modified_since:
                    try:
                        # Parse the If-Modified-Since header
                        if_modified_since_dt = parsedate_to_datetime(if_modified_since)
                        file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path), timezone.utc)

                        # Compare modification times
                        if file_modified_time <= if_modified_since_dt:
                            return generate_response(304)
                    except (TypeError, ValueError):
                        return generate_response(400)  # Malformed If-Modified-Since header

                with open(file_path, 'rb') as file:
                    content = file.read()
                return generate_response(200, content)

            else:
                return generate_response(404)

    return generate_response(400)

# Function to generate responses based on status codes
def generate_response(status_code, content=None):
    # Default responses for each status code
    if status_code == 200:
        response_line = "HTTP/1.1 200 OK\r\n"
        headers = "Content-Type: text/html\r\n\r\n"
        return response_line + headers + content.decode('utf-8')
    
    elif status_code == 304:
        response_line = "HTTP/1.1 304 Not Modified\r\n\r\n"
        return response_line

    elif status_code == 400:
        response_line = "HTTP/1.1 400 Bad Request\r\n\r\n"
        return response_line + "<h1>400 Bad Request</h1>"
    
    elif status_code == 404:
        response_line = "HTTP/1.1 404 Not Found\r\n\r\n"
        return response_line + "<h1>404 Not Found</h1>"

    elif status_code == 501:
        response_line = "HTTP/1.1 501 Not Implemented\r\n\r\n"
        return response_line + "<h1>501 Not Implemented</h1>"

while True:
    # Wait for a connection
    client_connection, client_address = server_socket.accept()

    # Receive the request from the client
    request = client_connection.recv(1024).decode('utf-8')
    print(request)  # For debugging, print the request

    # Generate the appropriate HTTP response
    response = handle_request(request)

    # Send the response to the client
    client_connection.sendall(response.encode('utf-8'))

    # Close the connection
    client_connection.close()
