# Generated: rep=1, llm=claude-3.5-sonnet
"""Authentication system - Clean Architecture + SOLID Principles."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# ═══════════════════════════════════════════════
# LAYER 1: ENTITIES (Domain Models)
# ═══════════════════════════════════════════════

@dataclass
class UserEntity:
    """Core domain entity."""
    id: int
        username: Any = None
    email: Any = None
    password_hash: Any = None
    created_at: Any = None


class UserRepositoryPort(ABC):
    """Domain port for persistence."""
    
    @abstractmethod
    def save(self, entity: UserEntity) -> UserEntity:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[UserEntity]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[UserEntity]:
        pass
    
    @abstractmethod
    def update(self, entity: UserEntity) -> Optional[UserEntity]:
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass


class ValidatorPort(ABC):
    """Domain port for validation."""
    @abstractmethod
    def validate(self, data: dict) -> List[str]:
        pass


# ═══════════════════════════════════════════════
# DTOs (Data Transfer Objects)
# ═══════════════════════════════════════════════

@dataclass
class CreateUserDTO:
    """DTO for creation requests."""
        username: Any = None
    email: Any = None
    password_hash: Any = None
    created_at: Any = None


@dataclass
class UserResponseDTO:
    """DTO for responses."""
    id: int
        username: Any = None
    email: Any = None
    password_hash: Any = None
    created_at: Any = None
    
    @classmethod
    def from_entity(cls, entity: UserEntity) -> "UserResponseDTO":
        return cls(id=entity.id, username=entity.username, email=entity.email, password_hash=entity.password_hash, created_at=entity.created_at)
    
    def to_dict(self) -> dict:
        return {"id": self.id, "username": self.username, "email": self.email, "password_hash": self.password_hash, "created_at": self.created_at}


# ═══════════════════════════════════════════════
# LAYER 2: USE CASES
# ═══════════════════════════════════════════════

class CreateUserUseCase:
    """SRP: only handles creation."""
    def __init__(self, repo: UserRepositoryPort, validator: ValidatorPort):
        self._repo = repo
        self._validator = validator
    
    def execute(self, dto: CreateUserDTO) -> UserResponseDTO:
        errors = self._validator.validate({
            "username": dto.username, "email": dto.email, "password_hash": dto.password_hash, "created_at": dto.created_at
        })
        if errors:
            raise ValueError("; ".join(errors))
        entity = UserEntity(id=0, username=dto.username, email=dto.email, password_hash=dto.password_hash, created_at=dto.created_at)
        saved = self._repo.save(entity)
        return UserResponseDTO.from_entity(saved)


class GetUserUseCase:
    """SRP: only handles retrieval."""
    def __init__(self, repo: UserRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> UserResponseDTO:
        entity = self._repo.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return UserResponseDTO.from_entity(entity)


class ListUsersUseCase:
    """SRP: only handles listing."""
    def __init__(self, repo: UserRepositoryPort):
        self._repo = repo
    
    def execute(self) -> List[UserResponseDTO]:
        return [UserResponseDTO.from_entity(e) for e in self._repo.find_all()]


class DeleteUserUseCase:
    """SRP: only handles deletion."""
    def __init__(self, repo: UserRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> None:
        if not self._repo.delete(entity_id):
            raise ValueError(f"{entity_id} not found")



# ═══════════════════════════════════════════════
# LAYER 3: INTERFACE ADAPTERS
# ═══════════════════════════════════════════════

class UserCreateValidator(ValidatorPort):
    """Concrete validator."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['username', 'email', 'password_hash']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors



class UserController:
    """REST adapter - maps HTTP to use cases."""
    def __init__(self, create_uc: CreateUserUseCase,
                 get_uc: GetUserUseCase,
                 list_uc: ListUsersUseCase,
                 delete_uc: DeleteUserUseCase):
        self._create = create_uc
        self._get = get_uc
        self._list = list_uc
        self._delete = delete_uc
    
    def handle(self, action: str, **kwargs) -> dict:
        try:
            if action == "create":
                dto = CreateUserDTO(**kwargs.get("data", {}))
                r = self._create.execute(dto)
                return {"status": 201, "body": r.to_dict()}
            elif action == "get":
                r = self._get.execute(kwargs["id"])
                return {"status": 200, "body": r.to_dict()}
            elif action == "list":
                rs = self._list.execute()
                return {"status": 200, "body": [r.to_dict() for r in rs]}
            elif action == "delete":
                self._delete.execute(kwargs["id"])
                return {"status": 204, "body": None}
            return {"status": 400, "body": "Unknown action"}
        except ValueError as e:
            return {"status": 400, "body": str(e)}


# ═══════════════════════════════════════════════
# LAYER 4: FRAMEWORKS & DRIVERS
# ═══════════════════════════════════════════════

class InMemoryUserRepository(UserRepositoryPort):
    """Framework-level persistence."""
    def __init__(self):
        self._store: Dict[int, UserEntity] = {}
        self._next_id = 1
    
    def save(self, entity: UserEntity) -> UserEntity:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[UserEntity]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[UserEntity]:
        return list(self._store.values())
    
    def update(self, entity: UserEntity) -> Optional[UserEntity]:
        if entity.id not in self._store:
            return None
        self._store[entity.id] = entity
        return entity
    
    def delete(self, entity_id: int) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False


def create_application() -> UserController:
    """Composition root - wire all dependencies."""
    repo = InMemoryUserRepository()
    validator = UserCreateValidator()
    create_uc = CreateUserUseCase(repo, validator)
    get_uc = GetUserUseCase(repo)
    list_uc = ListUsersUseCase(repo)
    delete_uc = DeleteUserUseCase(repo)
    return UserController(create_uc, get_uc, list_uc, delete_uc)
