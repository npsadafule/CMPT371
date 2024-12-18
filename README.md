# CMPT371 - Data Communications and Networking

# MP1 - Web and Proxy Server - Mini Project

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


# MP2 - Design, Implementation, and Testing of a Pipelined Reliable Transfer Protocol

## Overview

This project involves the design and implementation of a reliable data transfer protocol over UDP sockets in Python. The protocol incorporates flow control and congestion control mechanisms to ensure efficient and reliable communication over an unreliable network. Additionally, packet loss and corruption are simulated to test the robustness of the protocol under adverse network conditions.

## Features

- **Connection-Oriented Communication**: Implements a custom three-way handshake for connection establishment and a two-way handshake for termination.
- **Reliable Data Transfer**: Ensures data is delivered correctly and in order using sequence numbers, acknowledgments, checksums, and retransmissions.
- **Flow Control**: Utilizes a sliding window protocol to manage the flow of data between sender and receiver.
- **Congestion Control**: Implements congestion control mechanisms inspired by TCP's slow start and congestion avoidance phases.
- **Packet Loss and Corruption Simulation**: Simulates network unreliability by introducing random packet loss and corruption.
- **Performance Metrics**: Collects and visualizes performance metrics such as throughput, latency (RTT), and congestion window size over time.

## Project Structure

- `sender.py`: Contains the implementation of the sender side of the protocol.
- `receiver.py`: Contains the implementation of the receiver side of the protocol.
- `README.md`: This document.
- `CMPT_371_MP2.pdf`: Detailed report of the project, including design, implementation, testing procedures, and results.
- `figures/`: Directory containing figures and plots used in the report.
- `captures/`: Network traffic captures (`.pcap` files) demonstrating protocol operation.