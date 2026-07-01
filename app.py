import os
import threading
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import eventlet
from command_queue import CommandQueue
from attack_engine import AttackEngine
from planner_engine import PlannerEngine
from evolution_engine import EvolutionEngine
from api_integration import APIIntegration
from bot import start_bot

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

cmd_queue = CommandQueue()
attack_engine = AttackEngine(socketio)
planner_engine = PlannerEngine(socketio)
evolution_engine = EvolutionEngine(socketio)
api_integration = APIIntegration()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('chat_command')
def handle_chat_command(data):
    cmd = data.get('command', '').strip()
    if not cmd:
        return
    emit('chat_response', {'response': f'✅ Command received: {cmd}'})
    process_command(cmd, 'socket')

@socketio.on('strike')
def handle_strike(data):
    target = data.get('target', '').strip()
    level = data.get('level', 'standard')
    task = data.get('task', 'full')
    if not target:
        emit('log', {'msg': '❌ Target required', 'type': 'error'})
        return
    emit('log', {'msg': f'⚔️ Executing {level} level attack on {target} (Task: {task})', 'critical'})
    socketio.start_background_task(run_attack, target, level, task)

@socketio.on('evolve')
def handle_evolve(data):
    name = data.get('name', '').strip()
    if not name:
        emit('log', {'msg': '❌ Name required', 'type': 'error'})
        return
    result = evolution_engine.add_capability(name)
    emit('update', {'type': 'evolution', 'data': result})

def process_command(cmd, user_id):
    parts = cmd.lower().split()
    if not parts:
        return
    
    if parts[0] in ['strike', 'attack']:
        target = parts[1] if len(parts) > 1 else None
        level = parts[2] if len(parts) > 2 else 'standard'
        task = parts[3] if len(parts) > 3 else 'full'
        if target:
            socketio.start_background_task(run_attack, target, level, task)
    
    elif parts[0] in ['plan', 'planning']:
        target = parts[1] if len(parts) > 1 else 'Unknown'
        level = parts[2] if len(parts) > 2 else 'standard'
        plan = planner_engine.generate_plan(target, level)
        summary = planner_engine.get_plan_summary(plan)
        socketio.emit('update', {'type': 'plan', 'data': summary})
    
    elif parts[0] in ['add', 'evolve']:
        name = parts[1] if len(parts) > 1 else None
        if name:
            result = evolution_engine.add_capability(name)
            socketio.emit('update', {'type': 'evolution', 'data': result})
    
    elif parts[0] in ['status', 'stats']:
        status = evolution_engine.get_status()
        socketio.emit('update', {'type': 'status', 'data': status})

def run_attack(target, level, task):
    result = attack_engine.execute_attack(target, level, task)
    if result:
        data = attack_engine.get_data()
        if data:
            socketio.emit('update', {'type': 'exfil_data', 'data': data})
        socketio.emit('log', {'msg': '🏆 Attack completed successfully!', 'type': 'critical'})
    else:
        socketio.emit('log', {'msg': '⚠️ Attack failed.', 'type': 'error'})

if __name__ == '__main__':
    threading.Thread(target=start_bot, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
