from collections import defaultdict
from .config import MAX_HISTORY


class ConversationMemory:
    def __init__(self):
        self._sessions = defaultdict(list)

    def add(self, customer_id: str, role: str, content: str):
        history = self._sessions[customer_id]
        history.append({
            "role": role,
            "content": content,
        })

        if len(history) > MAX_HISTORY:
            del history[:-MAX_HISTORY]

    def get(self, customer_id: str):
        return list(self._sessions.get(customer_id, []))

    def clear(self, customer_id: str):
        self._sessions.pop(customer_id, None)
