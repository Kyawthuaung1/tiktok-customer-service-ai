from collections import defaultdict
from .config import MAX_HISTORY


class ConversationMemory:

    def __init__(self):
        self._sessions = defaultdict(list)
        self._active_products = {}

    def add(self, customer_id: str, role: str, content: str):
        history = self._sessions[customer_id]

        history.append({
            "role": role,
            "content": content,
        })

        if len(history) > MAX_HISTORY:
            del history[:-MAX_HISTORY]

    def get(self, customer_id: str):
        return list(
            self._sessions.get(customer_id, [])
        )

    def set_active_product(
        self,
        customer_id: str,
        product_name: str | None,
    ):
        if product_name:
            self._active_products[customer_id] = product_name
        else:
            self._active_products.pop(
                customer_id,
                None,
            )

    def get_active_product(self, customer_id: str):
        return self._active_products.get(
            customer_id
        )

    def clear(self, customer_id: str):
        self._sessions.pop(
            customer_id,
            None,
        )

        self._active_products.pop(
            customer_id,
            None,
        )
