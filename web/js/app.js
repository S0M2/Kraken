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

let ws = null;
let currentModule = 'ssh';

const menuItems = document.querySelectorAll('#module-menu li');
const moduleTitle = document.getElementById('module-title');
const portInput = document.getElementById('port');

menuItems.forEach(item => {
    item.addEventListener('click', (e) => {
        const li = e.target.closest('li');
        menuItems.forEach(i => i.classList.remove('active'));
        li.classList.add('active');
        
        currentModule = li.getAttribute('data-module');
        moduleTitle.innerText = li.innerText.trim();
        
        if(currentModule === 'ftp') portInput.placeholder = '21';
        else if(currentModule === 'ssh') portInput.placeholder = '22';
        else if(currentModule === 'wordpress') portInput.placeholder = '80/443';
        
        term.writeln(`\r\n\x1b[1;34m[*] Switched to mode: ${currentModule.toUpperCase()}\x1b[0m`);
    });
});

const form = document.getElementById('attack-form');
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const statusPulse = document.querySelector('.pulse');
const statusText = document.getElementById('system-status');

function setStatus(status, isRunning) {
    statusText.innerText = status;
    if(isRunning) {
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
    if(ws && ws.readyState === WebSocket.OPEN) return;

    term.clear();
    const target = document.getElementById('target').value;
    const port = document.getElementById('port').value;
    const threads = document.getElementById('threads').value;
    const users = document.getElementById('users').value;
    const passwords = document.getElementById('passwords').value;

    const config = {
        module: currentModule,
        args: {
            target: target,
            port: port || null,
            threads: threads,
            passwords: passwords
        }
    };
    
    // Some modules accept users file or username
    if (users) {
        if (users.includes('.txt') || users.includes('/')) {
            config.args.users = users;
        } else {
            config.args.username = users;
        }
    }

    startAttack(config);
});

stopBtn.addEventListener('click', () => {
    if(ws) {
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
        if(event.data instanceof Blob) {
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
