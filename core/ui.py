import os
import sys
import random
import time
from colorama import Fore, Style, init
import pyfiglet

init(autoreset=True)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner(text="Kraken Framework"):
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
    banner_color = random.choice(colors)
    banner = pyfiglet.figlet_format(text, font="slant")
    print(Style.BRIGHT + banner_color + banner)
    print(Style.RESET_ALL + Fore.WHITE + "="*80 + "\n")

def display_logo():
    clear = "\x1b[0m"
    colors = [36, 32, 34, 35, 31, 37]
    x = r"""
        ▄█   ▄█▄    ▄████████    ▄████████    ▄█   ▄█▄    ▄████████ ███▄▄▄▄   
        ███ ▄███▀   ███    ███   ███    ███   ███ ▄███▀   ███    ███ ███▀▀▀██▄ 
        ███▐██▀     ███    ███   ███    ███   ███▐██▀     ███    █▀  ███   ███ 
        ▄█████▀     ▄███▄▄▄▄██▀   ███    ███  ▄█████▀     ▄███▄▄▄     ███   ███ 
        ▀▀█████▄    ▀▀███▀▀▀▀▀   ▀███████████ ▀▀█████▄    ▀▀███▀▀▀     ███   ███ 
        ███▐██▄   ▀███████████   ███    ███   ███▐██▄     ███    █▄  ███   ███ 
        ███ ▀███▄   ███    ███   ███    ███   ███ ▀███▄   ███    ███ ███   ███ 
        ███   ▀█▀   ███    ███   ███    █▀    ███   ▀█▀   ██████████  ▀█   █▀  
        ▀           ███    ███                ▀                                
                                                                                                    
                    NOTE! : I'M NOT RESPONSIBLE FOR ANY ILLEGAL USAGE.
                    CODED BY : JASON13
                    VERSION : 2.0 (MODULAR)
    """
    for line in x.split("\n"):
        sys.stdout.write("\x1b[1;%dm%s%s\n" % (random.choice(colors), line, clear))
        time.sleep(0.02)

def status(msg):
    print(Fore.CYAN + "[*] " + msg)

def success(msg, end='\n'):
    print(Fore.GREEN + "[+] " + msg, end=end)

def error(msg):
    print(Fore.RED + "[-] " + msg)

def info(msg, end='\n'):
    print(Fore.WHITE + msg, end=end)
