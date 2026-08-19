# Generated: rep=3, llm=claude-3.5-sonnet
"""Caching system - Design Patterns + Dependency Injection."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class CacheEntry:
    """Domain entity."""
    def __init__(self, entity_id: int, key: Any = None, value: Any = None, created_at: Any = None, last_accessed: Any = None, ttl_seconds: Any = None):
        self.id = entity_id
                self.key = key
        self.value = value
        self.created_at = created_at
        self.last_accessed = last_accessed
        self.ttl_seconds = ttl_seconds
    
    def to_dict(self) -> dict:
        return {"id": self.id, "key": self.key, "value": self.value, "created_at": self.created_at, "last_accessed": self.last_accessed, "ttl_seconds": self.ttl_seconds}


class CacheEntryRepositoryInterface(ABC):
    """Abstract repository for cacheentry persistence."""
    
    @abstractmethod
    def save(self, entity: CacheEntry) -> CacheEntry:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[CacheEntry]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[CacheEntry]:
        pass
    
    @abstractmethod
    def update(self, entity: CacheEntry) -> Optional[CacheEntry]:
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass


class InMemoryCacheEntryRepository(CacheEntryRepositoryInterface):
    """In-memory implementation of repository."""
    
    def __init__(self):
        self._store: Dict[int, CacheEntry] = {}
        self._next_id = 1
    
    def save(self, entity: CacheEntry) -> CacheEntry:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[CacheEntry]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[CacheEntry]:
        return list(self._store.values())
    
    def update(self, entity: CacheEntry) -> Optional[CacheEntry]:
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


class CacheEntryCreateValidator(ValidationStrategy):
    """Validates creation data."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['key', 'value', 'created_at', 'last_accessed', 'ttl_seconds']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors








class CacheEntryService:
    """Business logic with dependency injection."""
    
    def __init__(self, repository: CacheEntryRepositoryInterface,
                 validator: ValidationStrategy):
        self._repository = repository
        self._validator = validator
    
    def create(self, data: dict) -> CacheEntry:
        errors = self._validator.validate(data)
        if errors:
            raise ValueError("; ".join(errors))
        entity = CacheEntry(entity_id=0, **{k: data.get(k) for k in ['key', 'value', 'created_at', 'last_accessed', 'ttl_seconds']})
        return self._repository.save(entity)
    
    def get(self, entity_id: int) -> CacheEntry:
        entity = self._repository.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return entity
    
    def list_all(self) -> List[CacheEntry]:
        return self._repository.find_all()
    
    def delete(self, entity_id: int) -> None:
        if not self._repository.delete(entity_id):
            raise ValueError(f"{entity_id} not found")


class CacheEntryController:
    """Controller with injected service."""
    
    def __init__(self, service: CacheEntryService):
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


def create_application() -> CacheEntryController:
    """Wire dependencies."""
    repo = InMemoryCacheEntryRepository()
    validator = CacheEntryCreateValidator()
    service = CacheEntryService(repo, validator)
    return CacheEntryController(service)
