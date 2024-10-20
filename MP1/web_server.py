import socket
import os
from datetime import datetime

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_socket.bind(('localhost', 8080))

# Listen for incoming connections
server_socket.listen(5)
print("Server is running on http://localhost:8080")

def handle_request(request):
    request_lines = request.splitlines()
    
    if len(request_lines) > 0:
        try:
            # Extract the request method, path, and HTTP version
            method, path, version = request_lines[0].split()
        except ValueError:
            # Malformed request line (e.g., missing elements)
            return generate_response(400)

        # Normalize the path (root as /index.html)
        if path == '/':
            path = '/index.html'

        # Check if the method is supported
        if method not in ['GET']:
            return generate_response(501)

        # Handle the GET method
        if method == 'GET':
            # Check for 'If-Modified-Since' header (for 304 response)
            if_modified_since = None
            for line in request_lines:
                if line.startswith("If-Modified-Since:"):
                    if_modified_since = line.split(":", 1)[1].strip()
                    break

            # Construct the file path
            file_path = 'www' + path
            
            # Check if the file exists
            if os.path.isfile(file_path):
                # Check if the file was modified since the date in the header
                if if_modified_since:
                    file_modified_time = os.path.getmtime(file_path)
                    file_modified_time = datetime.utcfromtimestamp(file_modified_time).strftime('%a, %d %b %Y %H:%M:%S GMT')

                    if file_modified_time <= if_modified_since:
                        return generate_response(304)

                # Return 200 OK with file content
                with open(file_path, 'rb') as file:
                    content = file.read()
                return generate_response(200, content)

            # If file not found, return 404
            else:
                return generate_response(404)

    # Return 400 if request is malformed
    return generate_response(400)

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
