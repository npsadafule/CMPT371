# Web and Proxy Server - Mini Project

## Overview
This Mini Project is focused on applying Web & HTTP and Socket Programming concepts to build a simple Web Server and a Proxy Server. The project explores various core topics, such as:

- HTTP Methods and Messages
- Socket Programming
- Connection Management
- Protocol Implementation & Analysis

## Project Structure

- `web_server.py`: The Python implementation of the web server.
- `proxy_server.py`: The Python implementation of the proxy server.
- `test.html`: HTML file used for testing server functionality.
- `README.md`: This documentation file.
- `report.pdf`: A detailed report covering specifications, implementation details, and testing procedures.

## Features

### 1. Web Server - Status Codes Implementation
The web server is designed to process HTTP requests and respond with the appropriate status codes:

- **200 OK**: The request was successful, and the server has returned the requested resource.
- **304 Not Modified**: The requested resource has not been modified since the specified date.
- **400 Bad Request**: The server cannot understand the request due to malformed syntax.
- **404 Not Found**: The requested resource could not be found on the server.
- **501 Not Implemented**: The server does not support the requested method.

The server implementation involves logic to determine which status code to respond with, based on the content of incoming requests. This logic, along with the HTTP requests used for testing, is fully documented in the report.

### 2. Web Server - Minimal Implementation and Testing
The web server is implemented using socket programming in Python. We use the socket module to create and manage TCP connections between the client and server. The server listens on a specified port, accepts incoming requests, and sends the appropriate response.

#### How to Test the Web Server
- **Testing Using a Browser**: 
  - Place the `test.html` file in the main directory of the server.
  - Start the web server and use a browser to access it via the URL:
    ```
    http://<IP_ADDRESS>:<PORT>/test.html
    ```
  - Replace `<IP_ADDRESS>` with your machine's IP address or `localhost`, and `<PORT>` with the port number the server is listening on.

- **Testing Using Curl/Telnet**:
  - The status codes can be tested using tools like `curl` and `telnet` to send HTTP requests directly to the server. Testing procedures for all status codes are included in the report, with screenshots showing server responses.

### 3. Proxy Server Implementation
The proxy server is an intermediary server that handles requests between a client and another web server. The key difference between a web server and a proxy server is that the proxy server forwards requests and responses between the client and the actual server.

The implemented proxy server is capable of handling basic HTTP requests from clients, forwarding them to the target server, and relaying the response back to the client.

### 4. Performance and Multi-Threading
- **Single-threaded vs Multi-threaded**: Initially, the server was implemented in a single-threaded model, which can handle only one request at a time. We expanded the server to support a multi-threaded model that allows handling multiple client requests simultaneously. This significantly improves the server's performance and response time.

- **Testing the Proxy Server**: We devised test cases to validate the proxy server's functionality, documented in the report with relevant outputs and screenshots.

### 5. Avoiding Head-of-Line (HOL) Blocking (Bonus Step)
To avoid Head-of-Line (HOL) blocking, we implemented frames to improve the handling of queued requests. This implementation reduces delays in processing, enhancing the overall user experience. Details of this step and its effect on performance are included in the report.

## Getting Started

### Prerequisites
- Python 3.x
- Basic understanding of socket programming
- Internet browser for testing
- Tools like `curl` or `telnet` for HTTP request testing

### Installation and Setup
1. Clone the repository:
   ```
   git clone https://github.com/your-username/mini-project-web-proxy.git
   cd mini-project-web-proxy
   ```

2. Run the Web Server:
   ```
   python3 web_server.py
   ```
   The web server will start listening on a specified port. You can modify the port number in the script if needed.

3. Access the Server:
   Open a web browser and navigate to `http://localhost:<PORT>/test.html` to see the hosted HTML page.

4. Run the Proxy Server:
   ```
   python3 proxy_server.py
   ```
   Set your browser to use the proxy by configuring the IP address and port number of the running proxy server.

## Deliverables
The project deliverables include:

1. **Web Server Code (`web_server.py`)**: Handles incoming HTTP requests and generates appropriate responses.
2. **Proxy Server Code (`proxy_server.py`)**: Acts as an intermediary server between the client and the target server.
3. **Modified Test Files (`test.html`)**: HTML files used to verify server functionality.
4. **Report (`report.pdf`)**: Contains specifications for status code generation, proxy requirements, testing procedures, and screenshots.
5. **README (`README.md`)**: This file, providing documentation and details about the project.

## Testing and Evaluation
- Testing was conducted using both browsers and command-line tools (`curl`, `telnet`), allowing verification of status codes and functionality.
- For the multi-threaded server, concurrent requests were tested, and server responses were verified to ensure correct implementation.

## Resources
The following resources were consulted during the project:

1. [RFC 7231 - HTTP/1.1 Semantics and Content](https://tools.ietf.org/html/rfc7231)
2. [Python Socket Programming Guide](https://docs.python.org/3/howto/sockets.html)
3. [Threading in Python](https://docs.python.org/3/library/threading.html)
4. [RFC 3040 - Web Proxy](https://www.ietf.org/rfc/rfc3040.txt)