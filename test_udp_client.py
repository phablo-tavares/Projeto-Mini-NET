import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(2.0)

while True:
    print("Testing UDP to 34.57.243.31:6000...")
    s.sendto(b"PING", ("34.57.243.31", 6000))
    time.sleep(2)
