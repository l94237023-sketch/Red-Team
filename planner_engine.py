import random
import time
from datetime import datetime

class PlannerEngine:
    def __init__(self, socketio=None):
        self.sio = socketio

    def _log(self, msg, type='info'):
        if self.sio:
            self.sio.emit('log', {'msg': f'📋 {msg}', 'type': type})

    def generate_plan(self, target, level="standard"):
        plan = {
            'target': target,
            'level': level,
            'timestamp': datetime.now().isoformat(),
            'phases': []
        }

        if level == "mobile":
            plan['phases'] = [
                {'name': 'OSINT', 'tasks': ['Search leaked databases', 'Enumerate emails', 'Find phone number']},
                {'name': 'Hacking', 'tasks': ['Phishing SMS', 'OTP Intercept', 'Gmail Recovery']},
                {'name': 'Exfil', 'tasks': ['Extract contacts', 'Export messages']}
            ]
        elif level == "gold":
            plan['phases'] = [
                {'name': 'Passive Recon', 'tasks': ['DNS analysis', 'Subdomain enumeration', 'Tech stack detection'], 'stealth': True},
                {'name': 'Slow Scan', 'tasks': ['Port scan (1 req/min)', 'Banner grabbing'], 'stealth': True},
                {'name': 'Stealth Exploit', 'tasks': ['Custom payloads', 'Low & Slow fuzzing'], 'stealth': True},
                {'name': 'Persistence', 'tasks': ['Worm deployment', 'Scheduled tasks'], 'stealth': True}
            ]
        else:
            plan['phases'] = [
                {'name': 'Recon', 'tasks': ['Port scan', 'Service detection']},
                {'name': 'Exploit', 'tasks': ['SQLi', 'RCE', 'LFI']},
                {'name': 'Post-Exploit', 'tasks': ['Data exfil', 'Backdoor']}
            ]
        
        self._log(f'✅ Plan generated for {target} ({level})', 'success')
        return plan

    def get_plan_summary(self, plan):
        summary = f"🎯 Target: {plan['target']}\n📊 Level: {plan['level']}\n📋 Phases:\n"
        for p in plan['phases']:
            stealth = "🕵️ Stealth" if p.get('stealth') else "⚡ Standard"
            summary += f"\n🔹 {p['name']} ({stealth})"
            for t in p['tasks']:
                summary += f"\n   - {t}"
        return summary
