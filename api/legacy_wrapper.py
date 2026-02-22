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
    elif 'url' in prompt_lower or 'target' in prompt_lower or 'site' in prompt_lower or 'ip address' in prompt_lower or 'host' in prompt_lower or 'server' in prompt_lower or 'domain' in prompt_lower or 'admin path' in prompt_lower:
        val = config.get('target', '')
    elif 'command' in prompt_lower:
        val = ""
    elif 'base dn' in prompt_lower:
        val = "dc=example,dc=com" # Hack for LDAP

    print(val) # Echo to the PTY
    return val

builtins.input = mocked_input

sys.argv = [script_path]
sys.path.insert(0, os.path.dirname(os.path.abspath(script_path)))

try:
    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()
    exec(code, {'__name__': '__main__', '__file__': script_path})
except Exception as e:
    print(f"\n[Wrapper Error] Failed to execute {script_path}: {str(e)}")
