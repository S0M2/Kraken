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

let ws = null;
const statusText = document.getElementById('system-status');
const statusPulse = document.querySelector('.pulse');
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');

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

const attackForm = document.getElementById('attack-form');

attackForm.addEventListener('submit', (e) => {
    e.preventDefault(); // <-- CRITICAL FIX: Prevent page reload

    if (ws) return;

    const config = {
        module: currentModule,
        args: {}
    };

    const target = document.getElementById('target').value;
    if (target) config.args.target = target;

    // Modern tools mapping
    if (['ssh', 'ftp', 'wordpress', 'wifi'].includes(currentModule)) {
        if (document.getElementById('port') && document.getElementById('port').parentElement.style.display !== 'none') {
            config.args.port = document.getElementById('port').value || null;
        }
        if (document.getElementById('users') && document.getElementById('users').parentElement.style.display !== 'none') {
            const userVal = document.getElementById('users').value;
            // Naive approach: if ends with .txt treat as file, else treat as single user
            if (userVal.toLowerCase().endsWith('.txt')) {
                config.args.users = userVal;
            } else if (userVal) {
                config.args.username = userVal;
            }
        }
        if (document.getElementById('passwords')) config.args.passwords = document.getElementById('passwords').value;
        if (document.getElementById('threads')) config.args.threads = document.getElementById('threads').value;

        if (currentModule === 'ssh' && document.getElementById('cmd')) {
            config.args.cmd = document.getElementById('cmd').value;
        }
        if (currentModule === 'wordpress' && document.getElementById('wp-submit')) {
            config.args.wp_submit_value = document.getElementById('wp-submit').value || 'Log In';
            config.args.wp_redirect_to = document.getElementById('wp-redirect') ? document.getElementById('wp-redirect').value : '';
        }
    } else {
        // Legacy Tools mapping
        const portVal = document.getElementById('port') ? document.getElementById('port').value : '';
        const threadVal = document.getElementById('threads') ? document.getElementById('threads').value : '';
        const userVal = document.getElementById('users') ? document.getElementById('users').value : '';
        const passVal = document.getElementById('passwords') ? document.getElementById('passwords').value : '';

        // If finder tool, no port or threads usually needed by legacy wrapper, but pass them anyway.
        // The wrapper will ignore what it doesn't need.
        config.args = {
            target: target,
            port: portVal,
            threads: threadVal,
            users: userVal,
            username: userVal,
            passwords: passVal
        };

        // Let main.py know exactly which file to execute
        config.script = `${currentModule}_bruteforce.py`;
        if (currentModule.includes('finder') || currentModule === 'directory' || currentModule === 'subdomain') {
            config.script = `${currentModule}_finder.py`;
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

document.getElementById('btn-export-csv').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/results');
        const data = await response.json();

        if (data.length === 0) {
            alert('No data to export.');
            return;
        }

        const headers = ['Timestamp', 'Module', 'Target', 'Username', 'Password'];
        const csvRows = [headers.join(',')];

        data.forEach(row => {
            const values = [
                row.timestamp,
                row.module,
                row.target,
                row.username,
                row.password || ''
            ];
            // Escape quotes and wrap in quotes for CSV safety
            csvRows.push(values.map(val => `"${String(val).replace(/"/g, '""')}"`).join(','));
        });

        const csvContent = "data:text/csv;charset=utf-8," + csvRows.join('\n');
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "kraken_compromised_credentials.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (error) {
        console.error("Export failed:", error);
        alert('Failed to export CSV. See console for details.');
    }
});

document.getElementById('btn-clear-history').addEventListener('click', async () => {
    if (confirm("🚨 WARNING 🚨\nAre you sure you want to permanently delete ALL compromised credentials from the database? This action cannot be undone.")) {
        try {
            const response = await fetch('/api/results', { method: 'DELETE' });
            if (response.ok) {
                term.writeln(`\r\n\x1b[1;31m[*] Database cleared by user.\x1b[0m`);
                loadHistory(); // Refresh the table
            } else {
                alert('Failed to clear database.');
            }
        } catch (error) {
            console.error("Clear DB failed:", error);
        }
    }
});
