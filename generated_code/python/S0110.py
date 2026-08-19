# Generated: rep=5, llm=claude-3.5-sonnet
"""Authentication system - Design Patterns + Dependency Injection."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class User:
    """Domain entity."""
    def __init__(self, entity_id: int, username: Any = None, email: Any = None, password_hash: Any = None, created_at: Any = None):
        self.id = entity_id
                self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
    
    def to_dict(self) -> dict:
        return {"id": self.id, "username": self.username, "email": self.email, "password_hash": self.password_hash, "created_at": self.created_at}


class UserRepositoryInterface(ABC):
    """Abstract repository for user persistence."""
    
    @abstractmethod
    def save(self, entity: User) -> User:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[User]:
        pass
    
    @abstractmethod
    def update(self, entity: User) -> Optional[User]:
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass


class InMemoryUserRepository(UserRepositoryInterface):
    """In-memory implementation of repository."""
    
    def __init__(self):
        self._store: Dict[int, User] = {}
        self._next_id = 1
    
    def save(self, entity: User) -> User:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[User]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[User]:
        return list(self._store.values())
    
    def update(self, entity: User) -> Optional[User]:
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


class UserCreateValidator(ValidationStrategy):
    """Validates creation data."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['username', 'email', 'password_hash', 'created_at']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors








class UserService:
    """Business logic with dependency injection."""
    
    def __init__(self, repository: UserRepositoryInterface,
                 validator: ValidationStrategy):
        self._repository = repository
        self._validator = validator
    
    def create(self, data: dict) -> User:
        errors = self._validator.validate(data)
        if errors:
            raise ValueError("; ".join(errors))
        entity = User(entity_id=0, **{k: data.get(k) for k in ['username', 'email', 'password_hash', 'created_at']})
        return self._repository.save(entity)
    
    def get(self, entity_id: int) -> User:
        entity = self._repository.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return entity
    
    def list_all(self) -> List[User]:
        return self._repository.find_all()
    
    def delete(self, entity_id: int) -> None:
        if not self._repository.delete(entity_id):
            raise ValueError(f"{entity_id} not found")


class UserController:
    """Controller with injected service."""
    
    def __init__(self, service: UserService):
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


def create_application() -> UserController:
    """Wire dependencies."""
    repo = InMemoryUserRepository()
    validator = UserCreateValidator()
    service = UserService(repo, validator)
    return UserController(service)
