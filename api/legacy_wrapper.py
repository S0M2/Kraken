import sys
import os
import builtins
import json

if len(sys.argv) < 3:
    print("Error: Missing arguments for legacy wrapper.")
    sys.exit(1)

script_path = sys.argv[1]
try:
    config = json.loads(sys.argv[2])
except:
    config = {}

def mocked_input(prompt=""):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    
    prompt_lower = prompt.lower()
    val = ""
    
    if 'threads' in prompt_lower:
        val = str(config.get('threads', '10'))
    elif 'port' in prompt_lower:
        # Check if the prompt mentions a default port and use it if no overriding port is provided
        val = str(config.get('port', ''))
    elif '(y/n)' in prompt_lower or 'yes/no' in prompt_lower:
        if 'list' in prompt_lower or 'username list' in prompt_lower:
            val = 'y' if config.get('users') else 'n'
        else:
            val = 'n' # Default to no for proxy or other queries
    elif 'password' in prompt_lower or 'credential' in prompt_lower or 'wordlist' in prompt_lower or 'passwords.txt' in prompt_lower:
        val = config.get('passwords', '')
    elif 'user file' in prompt_lower or 'username list' in prompt_lower or 'users.txt' in prompt_lower:
        val = config.get('users', '')
    elif 'username' in prompt_lower or 'single username' in prompt_lower:
        val = config.get('username', '')
    elif 'url' in prompt_lower or 'target' in prompt_lower or 'site' in prompt_lower or 'ip address' in prompt_lower or 'host' in prompt_lower or 'server' in prompt_lower or 'domain' in prompt_lower or 'admin path' in prompt_lower or 'ldap server address' in prompt_lower or 'voip server ip address' in prompt_lower:
        val = config.get('target', '')
    elif 'command' in prompt_lower:
        val = ""
    elif 'base dn' in prompt_lower:
        val = "dc=example,dc=com" # Hack for LDAP

    print(val) # Echo to the PTY
    return val

import urllib.request

original_open = builtins.open

class DBWriter:
    def __init__(self, fd, module_name, target):
        self.fd = fd
        self.module_name = module_name
        self.target = target

    def write(self, s):
        self.fd.write(s)
        if s.strip():
            try:
                data = json.dumps({
                    "module": self.module_name,
                    "target": self.target,
                    "username": s.strip(),
                    "password": ""
                }).encode('utf-8')
                req = urllib.request.Request("http://127.0.0.1:8000/api/results", data=data, headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=2)
            except Exception:
                pass
                
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fd.close()

    def __getattr__(self, attr):
        return getattr(self.fd, attr)

def mocked_open(file, mode='r', *args, **kwargs):
    fd = original_open(file, mode, *args, **kwargs)
    if ('w' in mode or 'a' in mode) and 'Results' in str(file):
        module_name = os.path.basename(script_path).replace(".py", "").replace("_bruteforce", "").replace("_finder", "").upper()
        target = config.get('target', 'Unknown Target')
        return DBWriter(fd, module_name, target)
    return fd

builtins.open = mocked_open
builtins.input = mocked_input

sys.argv = [script_path]
sys.path.insert(0, os.path.dirname(os.path.abspath(script_path)))

try:
    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()
    exec(code, {'__name__': '__main__', '__file__': script_path})
except Exception as e:
    print(f"\n[Wrapper Error] Failed to execute {script_path}: {str(e)}")
