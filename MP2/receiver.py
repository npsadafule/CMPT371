# receiver.py

import socket
import struct
import random
import threading
import time

# Constants
RECEIVER_ADDR = ('localhost', 12345)
TIMEOUT_INTERVAL = 2
LOSS_PROBABILITY = 0.1

# Packet Types
PACKET_TYPE_DATA = 0
PACKET_TYPE_SYN = 1
PACKET_TYPE_ACK = 2
PACKET_TYPE_FIN = 3

class Packet:
    def __init__(self, packet_type, seq_num, payload=b''):
        self.packet_type = packet_type  # 1 byte
        self.seq_num = seq_num          # 4 bytes
        self.payload = payload          # variable length
        self.checksum = 0               # 2 bytes, will be computed

    def compute_checksum(self):
        checksum = self.packet_type + self.seq_num
        checksum += sum(self.payload)
        return checksum & 0xFFFF  # Return as 16-bit value

    def pack(self):
        self.checksum = self.compute_checksum()
        header = struct.pack('!B I H', self.packet_type, self.seq_num, self.checksum)
        return header + self.payload

    @staticmethod
    def unpack(packet_bytes):
        packet_type, seq_num, checksum = struct.unpack('!B I H', packet_bytes[:7])
        payload = packet_bytes[7:]
        packet = Packet(packet_type, seq_num, payload)
        packet.checksum = checksum
        return packet

    def is_corrupt(self):
        return self.checksum != self.compute_checksum()

def rdt_receive():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECEIVER_ADDR)
    sock.settimeout(TIMEOUT_INTERVAL)

    expected_seq_num = 0
    received_data = []
    sender_address = None

    def establish_connection():
        nonlocal sender_address
        while True:
            try:
                packet_bytes, sender_addr = sock.recvfrom(4096)
                sender_address = sender_addr
                syn_packet = Packet.unpack(packet_bytes)
                if syn_packet.is_corrupt():
                    print("Received corrupt SYN packet.")
                    continue
                if syn_packet.packet_type == PACKET_TYPE_SYN and syn_packet.seq_num == 0:
                    # Send SYN-ACK
                    syn_ack_packet = Packet(PACKET_TYPE_SYN, 0).pack()
                    sock.sendto(syn_ack_packet, sender_address)
                    print("Sent SYN-ACK packet.")
                    # Wait for ACK
                    packet_bytes, _ = sock.recvfrom(4096)
                    ack_packet = Packet.unpack(packet_bytes)
                    if ack_packet.is_corrupt():
                        print("Received corrupt ACK packet.")
                        continue
                    if ack_packet.packet_type == PACKET_TYPE_ACK and ack_packet.seq_num == 0:
                        print("Connection established with sender.")
                        return True
            except socket.timeout:
                continue
        return False

    if not establish_connection():
        print("Failed to establish connection.")
        return

    connection_established = True
    while connection_established:
        try:
            packet_bytes, addr = sock.recvfrom(4096)
            if random.random() < LOSS_PROBABILITY:
                print("Simulating packet loss.")
                continue
            packet = Packet.unpack(packet_bytes)
            if packet.is_corrupt():
                print("Received corrupt data packet.")
                continue
            if packet.packet_type == PACKET_TYPE_FIN and packet.seq_num == 0:
                # Send FIN-ACK
                fin_ack_packet = Packet(PACKET_TYPE_FIN, 0).pack()
                sock.sendto(fin_ack_packet, sender_address)
                print("Connection terminated by sender.")
                connection_established = False
                break
            if packet.packet_type == PACKET_TYPE_DATA:
                if packet.seq_num == expected_seq_num:
                    data_str = packet.payload.decode()
                    print(f"Received data: {data_str} with sequence number {packet.seq_num}")
                    received_data.append(data_str)
                    # Send ACK
                    ack_packet = Packet(PACKET_TYPE_ACK, packet.seq_num).pack()
                    sock.sendto(ack_packet, sender_address)
                    expected_seq_num += 1
                else:
                    print(f"Unexpected sequence number. Expected {expected_seq_num}, got {packet.seq_num}")
                    # Resend ACK for the last acknowledged packet
                    ack_seq_num = expected_seq_num - 1 if expected_seq_num > 0 else 0
                    ack_packet = Packet(PACKET_TYPE_ACK, ack_seq_num).pack()
                    sock.sendto(ack_packet, sender_address)
        except socket.timeout:
            continue

    print("All data received.")
    sock.close()

if __name__ == "__main__":
    rdt_receive()
