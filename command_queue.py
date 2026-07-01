from collections import deque
import threading
from datetime import datetime

class CommandQueue:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CommandQueue, cls).__new__(cls)
                    cls._instance.commands = deque()
                    cls._instance.responses = deque()
        return cls._instance

    def add_command(self, user_id, command_text):
        self.commands.append({
            'user_id': user_id,
            'command': command_text,
            'timestamp': datetime.now().isoformat()
        })
        return True

    def get_next_command(self):
        if self.commands:
            return self.commands.popleft()
        return None

    def add_response(self, user_id, response):
        self.responses.append({
            'user_id': user_id,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
