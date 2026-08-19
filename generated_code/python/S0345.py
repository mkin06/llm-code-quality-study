# Generated: rep=5, llm=gpt-4o
"""Shopping cart - Design Patterns + Dependency Injection."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class Product:
    """Domain entity."""
    def __init__(self, entity_id: int, name: Any = None, price: Any = None, stock_quantity: Any = None, category: Any = None):
        self.id = entity_id
                self.name = name
        self.price = price
        self.stock_quantity = stock_quantity
        self.category = category
    
    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "price": self.price, "stock_quantity": self.stock_quantity, "category": self.category}


class ProductRepositoryInterface(ABC):
    """Abstract repository for product persistence."""
    
    @abstractmethod
    def save(self, entity: Product) -> Product:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[Product]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Product]:
        pass
    
    @abstractmethod
    def update(self, entity: Product) -> Optional[Product]:
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass


class InMemoryProductRepository(ProductRepositoryInterface):
    """In-memory implementation of repository."""
    
    def __init__(self):
        self._store: Dict[int, Product] = {}
        self._next_id = 1
    
    def save(self, entity: Product) -> Product:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[Product]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[Product]:
        return list(self._store.values())
    
    def update(self, entity: Product) -> Optional[Product]:
        if entity.id not in self._store:
            return None
        self._store[entity.id] = entity
        return entity
    
    def delete(self, entity_id: int) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False


class ValidationStrategy(ABC):
    """Strategy interface for validation."""
    @abstractmethod
    def validate(self, data: dict) -> List[str]:
        pass


class ProductCreateValidator(ValidationStrategy):
    """Validates creation data."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['name', 'price', 'stock_quantity', 'category']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors








class ProductService:
    """Business logic with dependency injection."""
    
    def __init__(self, repository: ProductRepositoryInterface,
                 validator: ValidationStrategy):
        self._repository = repository
        self._validator = validator
    
    def create(self, data: dict) -> Product:
        errors = self._validator.validate(data)
        if errors:
            raise ValueError("; ".join(errors))
        entity = Product(entity_id=0, **{k: data.get(k) for k in ['name', 'price', 'stock_quantity', 'category']})
        return self._repository.save(entity)
    
    def get(self, entity_id: int) -> Product:
        entity = self._repository.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return entity
    
    def list_all(self) -> List[Product]:
        return self._repository.find_all()
    
    def delete(self, entity_id: int) -> None:
        if not self._repository.delete(entity_id):
            raise ValueError(f"{entity_id} not found")


class ProductController:
    """Controller with injected service."""
    
    def __init__(self, service: ProductService):
        self._service = service
    
    def handle(self, action: str, **kwargs) -> dict:
        try:
            if action == "create":
                entity = self._service.create(kwargs.get("data", {}))
                return {"status": 201, "body": entity.to_dict()}
            elif action == "get":
                entity = self._service.get(kwargs["id"])
                return {"status": 200, "body": entity.to_dict()}
            elif action == "list":
                entities = self._service.list_all()
                return {"status": 200, "body": [e.to_dict() for e in entities]}
            elif action == "delete":
                self._service.delete(kwargs["id"])
                return {"status": 204, "body": None}
            return {"status": 400, "body": "Unknown action"}
        except ValueError as e:
            return {"status": 400, "body": str(e)}


def create_application() -> ProductController:
    """Wire dependencies."""
    repo = InMemoryProductRepository()
    validator = ProductCreateValidator()
    service = ProductService(repo, validator)
    return ProductController(service)
