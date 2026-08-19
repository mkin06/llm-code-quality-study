# Generated: rep=3, llm=claude-3.5-sonnet
"""Shopping cart - Basic separation of concerns."""


class ProductStorage:
    """Data storage for product records."""
    
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


class ProductValidator:
    """Validates product data."""
    
    def validate(self, data):
        errors = []
        for field in ['name', 'price', 'stock_quantity', 'category']:
            if not data.get(field):
                errors.append(f"{field} is required")
        if errors:
            raise ValueError("; ".join(errors))



class ProductService:
    """Business logic for product operations."""
    
    def __init__(self):
        self.storage = ProductStorage()
        self.validator = ProductValidator()
    
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


