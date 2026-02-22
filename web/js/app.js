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

let autoScroll = true;
let totalAttempts = 0;
let validHits = 0;
let lastAttemptsCount = 0;

document.getElementById('btn-autoscroll').addEventListener('click', function () {
    autoScroll = !autoScroll;
    this.classList.toggle('active', autoScroll);
    this.innerText = autoScroll ? '↓ Auto-Scroll' : '⏸ Auto-Scroll (Paused)';
});

document.getElementById('btn-clear').addEventListener('click', () => {
    term.clear();
});

setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        const speed = totalAttempts - lastAttemptsCount;
        document.getElementById('stat-speed').innerText = `${speed > 0 ? speed : 0} /s`;
        lastAttemptsCount = totalAttempts;
    }
}, 1000);

function startAttack(config) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/ws/run`;

    setStatus('Attacking...', true);
    document.getElementById('stats-panel').style.display = 'flex';
    document.querySelector('.dashboard').style.height = 'calc(100% - 150px)';

    // Reset Stats
    totalAttempts = 0;
    validHits = 0;
    lastAttemptsCount = 0;
    document.getElementById('stat-tested').innerText = '0';
    document.getElementById('stat-hits').innerText = '0';
    document.getElementById('stat-speed').innerText = '0 /s';

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        ws.send(JSON.stringify(config));
    };

    ws.onmessage = async (event) => {
        let text = event.data instanceof Blob ? await event.data.text() : event.data;
        term.write(text);
        if (autoScroll) {
            term.scrollToBottom();
        }

        const lowerText = text.toLowerCase();
        if (lowerText.includes('success') || lowerText.includes('found')) {
            validHits++;
            document.getElementById('stat-hits').innerText = validHits;
        }

        // Rough heuristic for attempt counting: carriage returns or newlines
        const lines = text.split(/\r|\n/);
        if (lines.length > 1) {
            totalAttempts += (lines.length - 1);
            document.getElementById('stat-tested').innerText = totalAttempts;
        }
    };

    ws.onclose = () => {
        setStatus('System Ready', false);
        ws = null;
        document.getElementById('stat-speed').innerText = '0 /s';
    };

    ws.onerror = () => {
        term.writeln(`\r\n\x1b[1;31m[-] API Connection Error.\x1b[0m`);
        setStatus('System Ready', false);
        document.getElementById('stat-speed').innerText = '0 /s';
    };
}

// --- History Panel Logic ---
const btnHistory = document.getElementById('btn-history');
const btnCloseHistory = document.getElementById('btn-close-history');
const historyPanel = document.getElementById('history-panel');
const dashboardViews = document.querySelectorAll('.dashboard, .stats-panel, .top-nav');

btnHistory.addEventListener('click', () => {
    dashboardViews.forEach(el => el.style.display = 'none');
    historyPanel.style.display = 'block';
    loadHistory();
});

btnCloseHistory.addEventListener('click', () => {
    historyPanel.style.display = 'none';
    document.querySelector('.top-nav').style.display = 'flex';
    document.querySelector('.dashboard').style.display = 'grid';
    // Hide stats panel unless an attack is currently running
    if (!ws) {
        document.getElementById('stats-panel').style.display = 'none';
        document.querySelector('.dashboard').style.height = '100%';
    } else {
        document.getElementById('stats-panel').style.display = 'flex';
    }
});

async function loadHistory() {
    const tbody = document.getElementById('results-tbody');
    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Loading data...</td></tr>';

    try {
        const response = await fetch('/api/results');
        const data = await response.json();

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No compromised credentials found yet.</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        data.forEach(row => {
            const tr = document.createElement('tr');

            // Format date nicely
            const dateObj = new Date(row.timestamp);
            const dateStr = dateObj.toLocaleString();

            tr.innerHTML = `
                <td>${dateStr}</td>
                <td><span style="color: var(--primary); font-weight: bold;">${row.module}</span></td>
                <td>${row.target}</td>
                <td style="color: #27c93f;">${row.username}</td>
                <td style="color: var(--magenta); font-weight: bold;">${row.password || 'N/A'}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #ff5f56;">Error loading database results.</td></tr>';
        console.error("Failed to fetch history:", error);
    }
}
