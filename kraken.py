import os
import sys
import time
import subprocess
import click

try:
    from rich.console import Console
    from rich.table import Table
    from rich.box import SIMPLE_HEAVY
    from colorama import Fore
    
    from core.ui import clear_console, display_logo, info
    from files import ftp_bruteforce, wordpress_bruteforce
except ImportError as e:
    print(f"Error: {e}. Please install the required modules using:")
    print("pip install -r requirements.txt")
    sys.exit(1)

console = Console()

def display_table():
    table = Table(box=SIMPLE_HEAVY)

    table.add_column("Network Tools", justify="left", style="cyan", no_wrap=True)
    table.add_column("Webapps Tools", justify="left", style="magenta", no_wrap=True)
    table.add_column("Finder Tools", justify="left", style="green", no_wrap=True)

    table.add_row("1. FTP Brute Force", "11. Cpanel Brute Force", "30. Admin Panel Finder")
    table.add_row("2. Kubernetes Brute Force", "12. Drupal Brute Force", "31. Directory Finder")
    table.add_row("3. LDAP Brute Force", "13. Joomla Brute Force", "32. Subdomain Finder")
    table.add_row("4. VOIP Brute Force", "15. Office365 Brute Force", "")
    table.add_row("5. SSH Brute Force", "16. Prestashop Brute Force", "")
    table.add_row("6. Telnet Brute Force", "17. OpenCart Brute Force", "")
    table.add_row("7. WiFi Brute Force", "18. WooCommerce Brute Force", "")
    table.add_row("8. RDP Brute Force", "19. WordPress Brute Force", "")

    table.add_row("", "", "")
    table.add_row("", "[bold red]-" * 15 + " 00. EXIT " + "-" * 15 + "[/bold red]", "", end_section=True)
    console.print(table)

def execute_legacy_script(script_name):
    script_path = os.path.join("files", script_name)
    if os.path.isfile(script_path):
        subprocess.call([sys.executable, script_path])
    else:
        print(Fore.RED + f"Script {script_name} not found in 'files' directory.")

def run_interactive():
    clear_console()
    display_logo()
    display_table()

    tools_mapping = {
        '1': 'ftp_bruteforce.py',
        '2': 'kubernetes_bruteforce.py',
        '3': 'ldap_bruteforce.py',
        '4': 'voip_bruteforce.py',
        '5': 'ssh_bruteforce.py',
        '6': 'telnet_bruteforce.py',
        '7': 'wifi_bruteforce.py',
        '8': 'rdp_bruteforce.py',
        '11': 'cpanel_bruteforce.py',
        '12': 'drupal_bruteforce.py',
        '13': 'joomla_bruteforce.py',
        '14': 'magento_bruteforce.py',
        '15': 'office365_bruteforce.py',
        '16': 'prestashop_bruteforce.py',
        '17': 'opencart_bruteforce.py',
        '18': 'woocommerce_bruteforce.py',
        '19': 'wordpress_bruteforce.py',
        '30': 'admin_panel_finder.py',
        '31': 'directory_finder.py',
        '32': 'subdomain_finder.py',
        '33': 'webshell_finder.py',
    }

    try:
        kraken = input("root@kraken:~# ")
        clear_console()

        if kraken in tools_mapping:
            
            if kraken == '1':
                ftp_bruteforce.run_interactive()
            elif kraken == '5':
                from files import ssh_bruteforce
                ssh_bruteforce.run_interactive()
            elif kraken == '19':
                wordpress_bruteforce.run_interactive()
            else:
                execute_legacy_script(tools_mapping[kraken])
        elif kraken == '00':
            print('\033[97m\nClosing Kraken\nPlease Wait...\033[1;m')
            time.sleep(2)
            sys.exit()
        else:
            print("Invalid Input!")
    except KeyboardInterrupt:
        print('\033[97m\nScript interrupted by user.\033[1;m')
        os._exit(0)

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """KRAKEN - The Ultimate Brute Force Framework."""
    if ctx.invoked_subcommand is None:
        run_interactive()

@cli.command()
@click.option('--target', required=True, help='Target FTP server IP address.')
@click.option('--users', help='Path to the username list.')
@click.option('--username', help='Single username to test.')
@click.option('--passwords', required=True, help='Path to the password list.')
@click.option('--threads', default=40, help='Number of threads (default 40).')
def ftp(target, users, username, passwords, threads):
    """Run FTP brute force module."""
    ftp_bruteforce.run(target, users, username, passwords, threads)

@cli.command()
@click.option('--target', required=True, help='Target WordPress URL.')
@click.option('--users', help='Path to the username list.')
@click.option('--username', help='Single username to test.')
@click.option('--passwords', required=True, help='Path to the password list.')
@click.option('--threads', default=10, help='Number of threads (default 10).')
def wordpress(target, users, username, passwords, threads):
    """Run WordPress brute force module."""
    wordpress_bruteforce.run(target, users, username, passwords, threads)

@cli.command()
@click.option('--target', required=True, help='Target SSH server IP address.')
@click.option('--port', default=22, help='Target SSH port (default 22).')
@click.option('--users', help='Path to the username list.')
@click.option('--username', help='Single username to test.')
@click.option('--passwords', required=True, help='Path to the password list.')
@click.option('--cmd', default='', help='Command to execute upon successful authentication.')
@click.option('--threads', default=40, help='Number of threads (default 40).')
def ssh(target, port, users, username, passwords, cmd, threads):
    """Run SSH brute force module."""
    from files import ssh_bruteforce
    ssh_bruteforce.run(target, port, users, username, passwords, cmd, threads)

if __name__ == "__main__":
    if sys.version_info < (3, 0):
        print("This script requires Python 3.")
        sys.exit(1)
    cli()
