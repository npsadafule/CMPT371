import socket
import threading

# Function to forward the request to the origin server and get the response
def forward_request(client_socket, request):
    try:
        # Connect to the origin server (e.g., example.com at port 80)
        origin_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        origin_server.connect(('httpbin.org', 80))

        # Forward the client's request to the origin server
        origin_server.sendall(request)

        # Receive the response from the origin server
        while True:
            response = origin_server.recv(4096)
            if len(response) == 0:
                break

            # Send the response back to the client
            client_socket.sendall(response)

    finally:
        # Close the connections
        origin_server.close()
        client_socket.close()

# Function to handle incoming requests from clients
def handle_client(client_socket):
    try:
        # Receive the client's request
        request = client_socket.recv(4096)
        print(f"Received request: {request.decode('utf-8')}")

        # Forward the request to the origin server
        forward_request(client_socket, request)

    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        client_socket.close()

# Create a TCP/IP socket for the proxy server
proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the proxy server to the port
proxy_server.bind(('0.0.0.0', 8888))  # Listening on port 8888 for proxy requests

# Listen for incoming connections
proxy_server.listen(10)
print("Proxy server is running on http://localhost:8888")

# Handle multiple client connections using threads
def start_proxy_server():
    while True:
        client_socket, client_address = proxy_server.accept()
        print(f"New connection from {client_address}")

        # Create a new thread for each client connection
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

# Start the proxy server
start_proxy_server()
