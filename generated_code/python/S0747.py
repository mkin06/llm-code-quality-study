# Generated: rep=2, llm=claude-3.5-sonnet
"""RBAC system - Design Patterns + Dependency Injection."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class Permission:
    """Domain entity."""
    def __init__(self, entity_id: int, resource: Any = None, action: Any = None, role: Any = None, granted: Any = None):
        self.id = entity_id
                self.resource = resource
        self.action = action
        self.role = role
        self.granted = granted
    
    def to_dict(self) -> dict:
        return {"id": self.id, "resource": self.resource, "action": self.action, "role": self.role, "granted": self.granted}


class PermissionRepositoryInterface(ABC):
    """Abstract repository for permission persistence."""
    
    @abstractmethod
    def save(self, entity: Permission) -> Permission:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[Permission]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Permission]:
        pass
    
    @abstractmethod
    def update(self, entity: Permission) -> Optional[Permission]:
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass


class InMemoryPermissionRepository(PermissionRepositoryInterface):
    """In-memory implementation of repository."""
    
    def __init__(self):
        self._store: Dict[int, Permission] = {}
        self._next_id = 1
    
    def save(self, entity: Permission) -> Permission:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[Permission]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[Permission]:
        return list(self._store.values())
    
    def update(self, entity: Permission) -> Optional[Permission]:
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


class PermissionCreateValidator(ValidationStrategy):
    """Validates creation data."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['resource', 'action', 'role', 'granted']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors








class PermissionService:
    """Business logic with dependency injection."""
    
    def __init__(self, repository: PermissionRepositoryInterface,
                 validator: ValidationStrategy):
        self._repository = repository
        self._validator = validator
    
    def create(self, data: dict) -> Permission:
        errors = self._validator.validate(data)
        if errors:
            raise ValueError("; ".join(errors))
        entity = Permission(entity_id=0, **{k: data.get(k) for k in ['resource', 'action', 'role', 'granted']})
        return self._repository.save(entity)
    
    def get(self, entity_id: int) -> Permission:
        entity = self._repository.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return entity
    
    def list_all(self) -> List[Permission]:
        return self._repository.find_all()
    
    def delete(self, entity_id: int) -> None:
        if not self._repository.delete(entity_id):
            raise ValueError(f"{entity_id} not found")


class PermissionController:
    """Controller with injected service."""
    
    def __init__(self, service: PermissionService):
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


def create_application() -> PermissionController:
    """Wire dependencies."""
    repo = InMemoryPermissionRepository()
    validator = PermissionCreateValidator()
    service = PermissionService(repo, validator)
    return PermissionController(service)
