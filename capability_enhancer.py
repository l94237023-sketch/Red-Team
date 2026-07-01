import os
import time
from datetime import datetime

class CapabilityEnhancer:
    def __init__(self, socketio=None):
        self.sio = socketio
        self.capabilities = self._scan_capabilities()
        self.generation = 0

    def _log(self, msg, type='info'):
        if self.sio:
            self.sio.emit('log', {'msg': f'🧬 {msg}', 'type': type})

    def _scan_capabilities(self):
        caps = []
        for f in os.listdir('.'):
            if f.endswith('_module.py') or f.endswith('_auditor.py'):
                caps.append(f.replace('.py', ''))
        return caps

    def add_capability(self, name):
        if f"{name}_module" in self.capabilities:
            return {'status': 'exists', 'message': f'⚠️ {name} already exists. Enhancement only adds new things!'}
        
        self._log(f'🛠️ Adding new capability: {name}', 'info')
        self.generation += 1
        
        code = f"""
class {name.capitalize()}Module:
    def __init__(self, socketio=None):
        self.sio = socketio
        self.name = "{name}"

    def execute(self, target):
        return {{"status": "executed", "target": target, "module": "{name}"}}
"""
        with open(f"{name}_module.py", 'w') as f:
            f.write(code)
        
        self._update_dashboard(name)
        self.capabilities = self._scan_capabilities()
        return {'status': 'success', 'message': f'✅ {name} added successfully!', 'generation': self.generation}

    def _update_dashboard(self, name):
        try:
            with open('templates/dashboard.html', 'r') as f:
                html = f.read()
            new_section = f"""
        <div class="card" id="card_{name}">
            <h4>🧩 {name.capitalize()}</h4>
            <p>Added by AI Enhancement (Gen {self.generation})</p>
            <button onclick="alert('Executing {name}...')">▶️ Execute</button>
        </div>
"""
            html = html.replace('<!-- DYNAMIC_CAPABILITIES -->', new_section + '\n<!-- DYNAMIC_CAPABILITIES -->')
            with open('templates/dashboard.html', 'w') as f:
                f.write(html)
        except:
            pass

    def get_status(self):
        return {
            'generation': self.generation,
            'capabilities': self.capabilities,
            'count': len(self.capabilities)
        }
