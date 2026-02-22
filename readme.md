<h1 align="center">
  <a href="">
    <picture>
      <source height="200" media="(prefers-color-scheme: dark)" srcset="https://i.imgur.com/iuvsqmp.png">
      <img height="200" alt="Kraken" src="https://i.imgur.com/dUFfdvk.png">
    </picture>
  </a>
  <br>
</h1>
<p align="center">
   A Python-based modular framework to centralize and streamline BruteForce Attacks
</p>

![screenshot](https://i.imgur.com/aYTy4Ll.gif)

---

## 🚀 What's New in v2.0 (MODULAR)

Kraken has been fundamentally rebuilt from the ground up to introduce a modern Object-Oriented Architecture, real-time web capabilities, and an integrated database system:

- **🕸 KRAKEN Web Dashboard**: A stunning, responsive Web UI with dark-mode glassmorphism. Control all 21 tools directly from your browser with real-time WebSocket terminal streaming and a live Global Progress Bar.
- **🗄️ Integrated SQLite Database**: No more messy `.txt` files in a Results folder. Every compromised credential is automatically saved into a centralized SQLite database. View, filter, clear, or export your findings to CSV directly from the Web Dashboard's "Results History" tab.
- **⚡️ Modern OOP Architecture & Click CLI**: The codebase has been refactored into a modular Object-Oriented structure. You can now use Kraken interactively, or script it directly from the command line using `click` (e.g., `python kraken.py ssh --target 127.0.0.1 --users users.txt --passwords pass.txt`).
- **📊 Rich Progress Bars**: Gone are the old manual percentage texts. Modules now utilize the professional `rich` library to display smooth loading bars, Estimated Time of Arrival (ETA), and valid hit counters.

---

## ⚠️  WARNING: LEGAL DISCLAIMER

This tool is intended for educational purposes only. The author is not responsible for any illegal use of this tool. Users are solely responsible 
for their actions.

---

## ⚙️ Installation

To install Kraken, follow these steps:

```bash
git clone https://github.com/S0M2/Kraken.git
cd Kraken
# It is highly recommended to use a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📖 Usage Modes

Kraken now offers three distinct ways to operate, catering to beginners and advanced professionals alike:

### 1. The Web Dashboard (Recommended)

Experience the beautiful, real-time graphical interface:
```bash
# Start the FastAPI backend server
uvicorn api.main:app --host 0.0.0.0 --port 8000
```
Then, open your web browser and navigate to **http://localhost:8000**. Select your target module, input your wordlists, and hit "Launch Attack". Watch the terminal stream live via WebSockets.

### 2. Interactive CLI Menu

The classic, user-friendly menu interface:
```bash
python kraken.py
```
This will display the familiar `root@kraken:~#` prompt and a table of the 21 available tools. Simply type the number corresponding to the tool you want to use.

### 3. Advanced Scripting CLI

Automation and direct execution using the robust `click` interface:
```bash
# Run the SSH module directly with arguments
python kraken.py ssh --target 192.168.1.1 --port 22 --username admin --passwords wordlists/passwords.txt --threads 20

# Get help for specific modules
python kraken.py ftp --help
```

---

## 🧰 Available Tools

1. **Network Tools:**
   - FTP Brute Force
   - Kubernetes Brute Force
   - LDAP Brute Force
   - VOIP Brute Force
   - SSH Brute Force
   - Telnet Brute Force
   - WiFi Brute Force
   - WPA3 Brute Force

2. **Webapps Tools:**
   - CPanel Brute Force
   - Drupal Brute Force
   - Joomla Brute Force
   - Magento Brute Force
   - Office365 Brute Force
   - Prestashop Brute Force
   - OpenCart Brute Force
   - WooCommerce Brute Force
   - WordPress Brute Force

3. **Finder Tools:**
   - Admin Panel Finder
   - Directory Finder
   - Subdomain Finder

---

## ⭐️ Show Your Support

If you find Kraken helpful or interesting, please consider giving us a star on GitHub. Your support helps promote the project and lets others know that it's worth checking out.

Thank you for your support! 🌟
