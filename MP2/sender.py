# sender.py

import socket
import struct
import random
import threading
import time
import matplotlib.pyplot as plt

# Constants
INITIAL_CWND = 1
INITIAL_SSTHRESH = 16
TIMEOUT_INTERVAL = 1.0
LOSS_PROBABILITY = 0.1
ERROR_PROBABILITY = 0.05
MAX_SEQ_NUM = 2**32 - 1

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

def rdt_send(sock, data_segments, receiver_address):
    base_seq_num = 0
    next_seq_num = 0
    window = {}
    timers = {}
    window_lock = threading.Lock()
    ack_event = threading.Event()

    congestion_window = INITIAL_CWND
    ssthresh = INITIAL_SSTHRESH

    # Performance Metrics Data
    send_times = {}
    ack_times = {}
    rtt_values = {}
    cwnd_values = []
    cwnd_times = []
    throughput_times = []
    throughput_values = []
    data_sent = 0
    start_time = time.time()

    def start_timer(seq_num):
        timers[seq_num] = threading.Timer(TIMEOUT_INTERVAL, handle_timeout, args=(seq_num,))
        timers[seq_num].start()

    def handle_timeout(seq_num):
        nonlocal congestion_window, ssthresh
        with window_lock:
            if seq_num in window:
                print(f"Timeout occurred for packet {seq_num}. Retransmitting.")
                send_packet(seq_num, window[seq_num])
                start_timer(seq_num)
                ssthresh = max(int(congestion_window // 2), 1)
                congestion_window = 1
                print(f"Updated ssthresh to {ssthresh} and reset congestion window to {congestion_window}")

    def send_packet(seq_num, payload):
        packet = Packet(PACKET_TYPE_DATA, seq_num, payload).pack()
        # Record send time
        send_times[seq_num] = time.time()
        if random.random() > LOSS_PROBABILITY:
            if random.random() < ERROR_PROBABILITY:
                packet = corrupt_packet(packet)
            sock.sendto(packet, receiver_address)
            print(f"Sent packet {seq_num}")
        else:
            print(f"Simulated packet loss for packet {seq_num}")

    def corrupt_packet(packet_bytes):
        # Introduce an error in the payload
        packet_list = list(packet_bytes)
        if len(packet_list) > 7:
            packet_list[7] ^= 0xFF  # Flip bits in the first byte of the payload
        return bytes(packet_list)

    def sending_thread():
        nonlocal next_seq_num, congestion_window, data_sent
        total_data_segments = len(data_segments)
        while base_seq_num < total_data_segments:
            with window_lock:
                while next_seq_num < base_seq_num + int(congestion_window) and next_seq_num < total_data_segments:
                    payload = data_segments[next_seq_num].encode()
                    send_packet(next_seq_num, payload)
                    data_sent += len(payload)
                    window[next_seq_num] = payload
                    start_timer(next_seq_num)
                    next_seq_num += 1
            ack_event.wait()
            ack_event.clear()
            # Record congestion window size and time
            cwnd_values.append(congestion_window)
            cwnd_times.append(time.time() - start_time)
        print("All data segments sent.")

    def ack_receiver_thread():
        nonlocal base_seq_num, congestion_window, ssthresh, data_sent
        sock.settimeout(2)
        last_throughput_calc_time = start_time
        bytes_acked_since_last = 0
        while base_seq_num < len(data_segments):
            try:
                packet_bytes, _ = sock.recvfrom(4096)
                packet = Packet.unpack(packet_bytes)
                if packet.is_corrupt():
                    print("Received corrupt ACK packet.")
                    continue
                if packet.packet_type == PACKET_TYPE_ACK:
                    ack_seq_num = packet.seq_num
                    with window_lock:
                        if ack_seq_num >= base_seq_num:
                            print(f"Received ACK for packet {ack_seq_num}")
                            # Record ACK receive time and calculate RTT
                            ack_times[ack_seq_num] = time.time()
                            rtt = ack_times[ack_seq_num] - send_times[ack_seq_num]
                            rtt_values[ack_seq_num] = rtt

                            # Cancel timers and remove acknowledged packets from the window
                            for seq in range(base_seq_num, ack_seq_num + 1):
                                if seq in timers:
                                    timers[seq].cancel()
                                    del timers[seq]
                                if seq in window:
                                    del window[seq]
                            # Update base sequence number
                            bytes_acked = 0
                            for seq in range(base_seq_num, ack_seq_num + 1):
                                bytes_acked += len(data_segments[seq])
                            base_seq_num = ack_seq_num + 1
                            bytes_acked_since_last += bytes_acked

                            # Congestion control
                            if congestion_window < ssthresh:
                                # Slow start phase
                                congestion_window += 1
                            else:
                                # Congestion avoidance phase
                                congestion_window += 1 / congestion_window
                            print(f"Updated congestion window size: {congestion_window}")

                            # Calculate throughput every second
                            current_time = time.time()
                            if current_time - last_throughput_calc_time >= 1:
                                throughput = bytes_acked_since_last * 8 / (current_time - last_throughput_calc_time)  # bits per second
                                throughput_times.append(current_time - start_time)
                                throughput_values.append(throughput)
                                bytes_acked_since_last = 0
                                last_throughput_calc_time = current_time

                            ack_event.set()
            except socket.timeout:
                continue

    def establish_connection():
        # Send SYN packet
        syn_packet = Packet(PACKET_TYPE_SYN, 0).pack()
        sock.sendto(syn_packet, receiver_address)
        print("Sent SYN packet to initiate connection.")
        sock.settimeout(5)
        try:
            packet_bytes, _ = sock.recvfrom(4096)
            syn_ack_packet = Packet.unpack(packet_bytes)
            if syn_ack_packet.is_corrupt():
                print("Received corrupt SYN-ACK packet.")
                return False
            if syn_ack_packet.packet_type == PACKET_TYPE_SYN and syn_ack_packet.seq_num == 0:
                # Send ACK packet
                ack_packet = Packet(PACKET_TYPE_ACK, 0).pack()
                sock.sendto(ack_packet, receiver_address)
                print("Sent ACK packet. Connection established.")
                return True
        except socket.timeout:
            print("Timeout waiting for SYN-ACK.")
            return False
        return False

    def terminate_connection():
        # Send FIN packet
        fin_packet = Packet(PACKET_TYPE_FIN, 0).pack()
        sock.sendto(fin_packet, receiver_address)
        print("Sent FIN packet to terminate connection.")
        sock.settimeout(5)
        try:
            packet_bytes, _ = sock.recvfrom(4096)
            fin_ack_packet = Packet.unpack(packet_bytes)
            if fin_ack_packet.is_corrupt():
                print("Received corrupt FIN-ACK packet.")
                return False
            if fin_ack_packet.packet_type == PACKET_TYPE_FIN and fin_ack_packet.seq_num == 0:
                print("Connection terminated gracefully.")
                return True
        except socket.timeout:
            print("Timeout waiting for FIN-ACK.")
            return False
        return False

    if not establish_connection():
        print("Failed to establish connection with receiver.")
        return

    send_thread = threading.Thread(target=sending_thread)
    ack_thread = threading.Thread(target=ack_receiver_thread)
    send_thread.start()
    ack_thread.start()
    send_thread.join()
    ack_thread.join()

    if not terminate_connection():
        print("Failed to terminate connection properly.")

    # Plotting Performance Metrics
    plot_performance_metrics(rtt_values, cwnd_values, cwnd_times, throughput_times, throughput_values)

def plot_performance_metrics(rtt_values, cwnd_values, cwnd_times, throughput_times, throughput_values):
    import matplotlib.pyplot as plt

    # Plot RTT
    seq_nums = sorted(rtt_values.keys())
    rtt_list = [rtt_values[seq_num]*1000 for seq_num in seq_nums]  # Convert to milliseconds
    plt.figure()
    plt.plot(seq_nums, rtt_list, marker='o')
    plt.xlabel('Packet Sequence Number')
    plt.ylabel('RTT (ms)')
    plt.title('RTT for Each Packet')
    plt.grid(True)
    plt.savefig('latency_plot.png')
    plt.close()

    # Plot Congestion Window
    plt.figure()
    plt.plot(cwnd_times, cwnd_values, marker='o')
    plt.xlabel('Time (s)')
    plt.ylabel('Congestion Window Size (packets)')
    plt.title('Congestion Window Over Time')
    plt.grid(True)
    plt.savefig('cwnd_plot.png')
    plt.close()

    # Plot Throughput
    plt.figure()
    plt.plot(throughput_times, throughput_values, marker='o')
    plt.xlabel('Time (s)')
    plt.ylabel('Throughput (bps)')
    plt.title('Throughput Over Time')
    plt.grid(True)
    plt.savefig('throughput_plot.png')
    plt.close()

if __name__ == "__main__":
    receiver_addr = ('localhost', 12345)
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Prepare the data segments to send
    messages = [f"Message part {i}" for i in range(1, 100)]

    rdt_send(sender_socket, messages, receiver_addr)
    sender_socket.close()
