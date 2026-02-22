const term = new Terminal({
    theme: {
        background: 'transparent',
        foreground: '#e2e8f0',
        cursor: '#00f0ff',
        black: '#000000',
        red: '#ff5f56',
        green: '#27c93f',
        yellow: '#ffbd2e',
        blue: '#00f0ff',
        magenta: '#ff0055',
        cyan: '#00f0ff',
        white: '#ffffff',
    },
    fontFamily: 'JetBrains Mono, monospace',
    fontSize: 14,
    convertEol: true,
    cursorBlink: true,
    disableStdin: true
});

term.open(document.getElementById('terminal-container'));
term.writeln('\x1b[1;36m[KRAKEN]\x1b[0m Web Console Initialized.');
term.writeln('Awaiting module configuration...');

const modulesConfig = {
    'ftp': { name: 'FTP Brute Force', icon: '📂', type: 'network', port: '21', needsUsers: true, needsPasswords: true },
    'kubernetes': { name: 'Kubernetes Brute', icon: '⚙️', type: 'network', port: '', needsUsers: true, needsPasswords: true },
    'ldap': { name: 'LDAP Brute Force', icon: '📇', type: 'network', port: '389', needsUsers: true, needsPasswords: true },
    'voip': { name: 'VOIP Brute Force', icon: '📞', type: 'network', port: '5060', needsUsers: true, needsPasswords: true },
    'ssh': { name: 'SSH Brute Force', icon: '💻', type: 'network', port: '22', needsUsers: true, needsPasswords: true },
    'telnet': { name: 'Telnet Brute Force', icon: '📟', type: 'network', port: '23', needsUsers: true, needsPasswords: true },
    'wifi': { name: 'WiFi Brute Force', icon: '📶', type: 'network', port: '', needsUsers: false, needsPasswords: true },
    'rdp': { name: 'RDP Brute Force', icon: '🖥️', type: 'network', port: '3389', needsUsers: true, needsPasswords: true },

    'cpanel': { name: 'Cpanel Brute Force', icon: '🎛️', type: 'webapp', port: '2083', needsUsers: true, needsPasswords: true },
    'drupal': { name: 'Drupal Brute Force', icon: '💧', type: 'webapp', port: '', needsUsers: true, needsPasswords: true },
    'joomla': { name: 'Joomla Brute Force', icon: '🧩', type: 'webapp', port: '', needsUsers: true, needsPasswords: true },
    'magento': { name: 'Magento Brute Force', icon: '🛒', type: 'webapp', port: '', needsUsers: true, needsPasswords: true },
    'office365': { name: 'Office365 Brute', icon: '✉️', type: 'webapp', port: '', needsUsers: false, needsPasswords: true, passLabel: "Cred List (email:pass)" },
    'prestashop': { name: 'PrestaShop Brute', icon: '🛍️', type: 'webapp', port: '', needsUsers: true, needsPasswords: true },
    'opencart': { name: 'OpenCart Brute', icon: '🛒', type: 'webapp', port: '', needsUsers: true, needsPasswords: true },
    'woocommerce': { name: 'WooCommerce Brute', icon: '📦', type: 'webapp', port: '', needsUsers: true, needsPasswords: true },
    'wordpress': { name: 'WordPress Brute', icon: '🌐', type: 'webapp', port: '', needsUsers: true, needsPasswords: true },

    'admin_panel_finder': { name: 'Admin Panel Finder', icon: '🕵️', type: 'finder', port: '', needsUsers: false, needsPasswords: true, passLabel: 'Wordlist path' },
    'directory_finder': { name: 'Directory Finder', icon: '📁', type: 'finder', port: '', needsUsers: false, needsPasswords: true, passLabel: 'Wordlist path' },
    'subdomain_finder': { name: 'Subdomain Finder', icon: '🔗', type: 'finder', port: '', needsUsers: false, needsPasswords: true, passLabel: 'Wordlist path' },
    'webshell_finder': { name: 'Webshell Finder', icon: '🦠', type: 'finder', port: '', needsUsers: false, needsPasswords: true, passLabel: 'Wordlist path' },
};

let currentModule = 'ssh';

const moduleMenu = document.getElementById('module-menu');
const moduleTitle = document.getElementById('module-title');
const portInput = document.getElementById('port');
const usersGroup = document.getElementById('users').closest('.form-group');
const passwordsGroup = document.getElementById('passwords').closest('.form-group');
const passLabel = passwordsGroup.querySelector('label');
const portGroup = portInput.closest('.form-group');

// Generate Sidebar
Object.entries(modulesConfig).forEach(([key, config]) => {
    const li = document.createElement('li');
    li.dataset.module = key;
    if (key === currentModule) li.classList.add('active');
    li.innerHTML = `<span class="icon">${config.icon}</span> ${config.name}`;

    li.addEventListener('click', () => {
        document.querySelectorAll('#module-menu li').forEach(i => i.classList.remove('active'));
        li.classList.add('active');

        currentModule = key;
        const mod = modulesConfig[key];
        moduleTitle.innerText = mod.name;

        portInput.placeholder = mod.port;
        if (mod.port === '') {
            portInput.value = '';
            portGroup.style.opacity = '0.3';
            portInput.disabled = true;
        } else {
            portGroup.style.opacity = '1';
            portInput.disabled = false;
        }

        usersGroup.style.display = mod.needsUsers ? 'block' : 'none';
        passwordsGroup.style.display = mod.needsPasswords ? 'block' : 'none';
        passLabel.innerHTML = mod.passLabel ? `${mod.passLabel} <span>*</span>` : `Password List <span>*</span>`;

        term.writeln(`\r\n\x1b[1;34m[*] Switched to mode: ${mod.name.toUpperCase()}\x1b[0m`);
    });

    moduleMenu.appendChild(li);
});

function setStatus(status, isRunning) {
    statusText.innerText = status;
    if (isRunning) {
        statusPulse.style.backgroundColor = '#ffbd2e';
        statusPulse.style.boxShadow = '0 0 10px #ffbd2e';
        startBtn.style.display = 'none';
        stopBtn.style.display = 'flex';
    } else {
        statusPulse.style.backgroundColor = '#27c93f';
        statusPulse.style.boxShadow = '0 0 10px #27c93f';
        startBtn.style.display = 'flex';
        stopBtn.style.display = 'none';
    }
}

form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (ws && ws.readyState === WebSocket.OPEN) return;

    term.clear();
    const target = document.getElementById('target').value;
    const port = document.getElementById('port').value;
    const threads = document.getElementById('threads').value;
    const users = document.getElementById('users').value;
    const passwords = document.getElementById('passwords').value;

    const modConfig = modulesConfig[currentModule];
    const scriptName = modConfig.script || `${currentModule}_bruteforce.py`;

    const config = {
        module: currentModule,
        script: scriptName,
        args: {
            target: target,
            port: port || null,
            threads: threads,
            passwords: passwords
        }
    };

    if (users) {
        if (users.includes('.txt') || users.includes('/')) {
            config.args.users = users;
            config.args.is_list = true;
        } else {
            config.args.username = users;
            config.args.is_list = false;
        }
    }

    startAttack(config);
});

stopBtn.addEventListener('click', () => {
    if (ws) {
        // Just closing the socket causes Python's WebSocketDisconnect exception, 
        // which triggers process.terminate()
        ws.close();
        term.writeln('\r\n\x1b[1;31m[!] Attack aborted manually.\x1b[0m');
        setStatus('System Ready', false);
    }
});

function startAttack(config) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/ws/run`;

    setStatus('Attacking...', true);
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        ws.send(JSON.stringify(config));
    };

    ws.onmessage = async (event) => {
        if (event.data instanceof Blob) {
            const text = await event.data.text();
            term.write(text);
        } else {
            term.write(event.data);
        }
    };

    ws.onclose = () => {
        setStatus('System Ready', false);
        ws = null;
    };

    ws.onerror = () => {
        term.writeln(`\r\n\x1b[1;31m[-] API Connection Error.\x1b[0m`);
        setStatus('System Ready', false);
    };
}
