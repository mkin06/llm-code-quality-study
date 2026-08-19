# Generated: rep=5, llm=claude-3.5-sonnet
"""Caching system - Basic separation of concerns."""


class CacheEntryStorage:
    """Data storage for cacheentry records."""
    
    def __init__(self):
        self._items = {}
        self._next_id = 1
    
    def save(self, data):
        item_id = self._next_id
        self._next_id += 1
        item = {"id": item_id, **data}
        self._items[item_id] = item
        return item
    
    def find_by_id(self, item_id):
        return self._items.get(item_id)
    
    def find_all(self):
        return list(self._items.values())
    
    def update(self, item_id, updates):
        if item_id not in self._items:
            return None
        for k, v in updates.items():
            if v is not None:
                self._items[item_id][k] = v
        return self._items[item_id]
    
    def delete(self, item_id):
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False


class CacheEntryValidator:
    """Validates cacheentry data."""
    
    def validate(self, data):
        errors = []
        for field in ['key', 'value', 'created_at', 'last_accessed', 'ttl_seconds']:
            if not data.get(field):
                errors.append(f"{field} is required")
        if errors:
            raise ValueError("; ".join(errors))



class CacheEntryService:
    """Business logic for cacheentry operations."""
    
    def __init__(self):
        self.storage = CacheEntryStorage()
        self.validator = CacheEntryValidator()
    
    def create(self, data):
        self.validator.validate(data)
        return self.storage.save(data)
    
    def get(self, item_id):
        item = self.storage.find_by_id(item_id)
        if not item:
            raise ValueError(f"{item_id} not found")
        return item
    
    def list_all(self):
        return self.storage.find_all()
    
    def update(self, item_id, data):
        result = self.storage.update(item_id, data)
        if not result:
            raise ValueError(f"{item_id} not found")
        return result
    
    def delete(self, item_id):
        if not self.storage.delete(item_id):
            raise ValueError(f"{item_id} not found")


