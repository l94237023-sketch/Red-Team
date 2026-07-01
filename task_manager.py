from collections import deque
import threading
from datetime import datetime

class TaskManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TaskManager, cls).__new__(cls)
                    cls._instance.tasks = deque()
                    cls._instance.responses = deque()
        return cls._instance

    def add_task(self, user_id, command_text):
        self.tasks.append({
            'user_id': user_id,
            'command': command_text,
            'timestamp': datetime.now().isoformat()
        })
        return True

    def get_next_task(self):
        if self.tasks:
            return self.tasks.popleft()
        return None

    def add_response(self, user_id, response):
        self.responses.append({
            'user_id': user_id,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
