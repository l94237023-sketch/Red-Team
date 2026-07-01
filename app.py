import os
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import eventlet
from task_manager import TaskManager
from security_auditor import SecurityAuditor
from assessment_planner import AssessmentPlanner
from capability_enhancer import CapabilityEnhancer
from ai_service_broker import AIServiceBroker
from telegram_connector import start_bot

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

task_manager = TaskManager()
auditor = SecurityAuditor(socketio)
planner = AssessmentPlanner(socketio)
enhancer = CapabilityEnhancer(socketio)
ai_broker = AIServiceBroker()

@app.route('/')
def index():
    return render_template('dashboard.html')

@socketio.on('chat_command')
def handle_chat_command(data):
    cmd = data.get('command', '').strip()
    if not cmd:
        return
    emit('chat_response', {'response': f'✅ Command received: {cmd}'})
    process_command(cmd, 'socket')

@socketio.on('audit')
def handle_audit(data):
    target = data.get('target', '').strip()
    level = data.get('level', 'standard')
    task = data.get('task', 'full')
    if not target:
        emit('log', {'msg': '❌ Target required', 'type': 'error'})
        return
    emit('log', {'msg': f'🔍 Executing {level} level audit on {target} (Task: {task})', 'critical'})
    socketio.start_background_task(run_audit, target, level, task)

@socketio.on('enhance')
def handle_enhance(data):
    name = data.get('name', '').strip()
    if not name:
        emit('log', {'msg': '❌ Name required', 'type': 'error'})
        return
    result = enhancer.add_capability(name)
    emit('update', {'type': 'enhancement', 'data': result})

def process_command(cmd, user_id):
    parts = cmd.lower().split()
    if not parts:
        return
    if parts[0] in ['audit', 'probe']:
        target = parts[1] if len(parts) > 1 else None
        level = parts[2] if len(parts) > 2 else 'standard'
        task = parts[3] if len(parts) > 3 else 'full'
        if target:
            socketio.start_background_task(run_audit, target, level, task)
    elif parts[0] in ['plan']:
        target = parts[1] if len(parts) > 1 else 'Unknown'
        level = parts[2] if len(parts) > 2 else 'standard'
        plan = planner.generate_plan(target, level)
        summary = planner.get_plan_summary(plan)
        socketio.emit('update', {'type': 'plan', 'data': summary})
    elif parts[0] in ['add', 'enhance']:
        name = parts[1] if len(parts) > 1 else None
        if name:
            result = enhancer.add_capability(name)
            socketio.emit('update', {'type': 'enhancement', 'data': result})
    elif parts[0] in ['status']:
        status = enhancer.get_status()
        socketio.emit('update', {'type': 'status', 'data': status})

def run_audit(target, level, task):
    result = auditor.run_audit(target, level, task)
    if result:
        data = auditor.get_data()
        if data:
            socketio.emit('update', {'type': 'extracted_data', 'data': data})
        socketio.emit('log', {'msg': '🏆 Audit completed successfully!', 'type': 'critical'})
    else:
        socketio.emit('log', {'msg': '⚠️ Audit failed.', 'type': 'error'})

if __name__ == '__main__':
    threading.Thread(target=start_bot, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
