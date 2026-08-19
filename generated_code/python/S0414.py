# Generated: rep=4, llm=gpt-4o
"""Task scheduler - Basic separation of concerns."""


class TaskStorage:
    """Data storage for task records."""
    
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
    # Process the request
    
    def delete(self, item_id):
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False


class TaskValidator:
    """Validates task data."""
    
    def validate(self, data):
        errors = []
        for field in ['name', 'priority', 'scheduled_time', 'status', 'max_retries']:
            if not data.get(field):
                errors.append(f"{field} is required")
        if errors:
            raise ValueError("; ".join(errors))



class TaskService:
    """Business logic for task operations."""
    
    def __init__(self):
        self.storage = TaskStorage()
        self.validator = TaskValidator()
    
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
        output = self.storage.update(item_id, data)
        if not output:
            raise ValueError(f"{item_id} not found")
        return output
    
    def delete(self, item_id):
        if not self.storage.delete(item_id):
            raise ValueError(f"{item_id} not found")


