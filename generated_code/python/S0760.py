# Generated: rep=5, llm=claude-3.5-sonnet
"""RBAC system - Clean Architecture + SOLID Principles."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# ═══════════════════════════════════════════════
# LAYER 1: ENTITIES (Domain Models)
# ═══════════════════════════════════════════════

@dataclass
class PermissionEntity:
    """Core domain entity."""
    id: int
        resource: Any = None
    action: Any = None
    role: Any = None
    granted: Any = None


class PermissionRepositoryPort(ABC):
    """Domain port for persistence."""
    
    @abstractmethod
    def save(self, entity: PermissionEntity) -> PermissionEntity:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[PermissionEntity]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[PermissionEntity]:
        pass
    
    @abstractmethod
    def update(self, entity: PermissionEntity) -> Optional[PermissionEntity]:
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
class CreatePermissionDTO:
    """DTO for creation requests."""
        resource: Any = None
    action: Any = None
    role: Any = None
    granted: Any = None


@dataclass
class PermissionResponseDTO:
    """DTO for responses."""
    id: int
        resource: Any = None
    action: Any = None
    role: Any = None
    granted: Any = None
    
    @classmethod
    def from_entity(cls, entity: PermissionEntity) -> "PermissionResponseDTO":
        return cls(id=entity.id, resource=entity.resource, action=entity.action, role=entity.role, granted=entity.granted)
    
    def to_dict(self) -> dict:
        return {"id": self.id, "resource": self.resource, "action": self.action, "role": self.role, "granted": self.granted}


# ═══════════════════════════════════════════════
# LAYER 2: USE CASES
# ═══════════════════════════════════════════════

class CreatePermissionUseCase:
    """SRP: only handles creation."""
    def __init__(self, repo: PermissionRepositoryPort, validator: ValidatorPort):
        self._repo = repo
        self._validator = validator
    
    def execute(self, dto: CreatePermissionDTO) -> PermissionResponseDTO:
        errors = self._validator.validate({
            "resource": dto.resource, "action": dto.action, "role": dto.role, "granted": dto.granted
        })
        if errors:
            raise ValueError("; ".join(errors))
        entity = PermissionEntity(id=0, resource=dto.resource, action=dto.action, role=dto.role, granted=dto.granted)
        saved = self._repo.save(entity)
        return PermissionResponseDTO.from_entity(saved)


class GetPermissionUseCase:
    """SRP: only handles retrieval."""
    def __init__(self, repo: PermissionRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> PermissionResponseDTO:
        entity = self._repo.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return PermissionResponseDTO.from_entity(entity)


class ListPermissionsUseCase:
    """SRP: only handles listing."""
    def __init__(self, repo: PermissionRepositoryPort):
        self._repo = repo
    
    def execute(self) -> List[PermissionResponseDTO]:
        return [PermissionResponseDTO.from_entity(e) for e in self._repo.find_all()]


class DeletePermissionUseCase:
    """SRP: only handles deletion."""
    def __init__(self, repo: PermissionRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> None:
        if not self._repo.delete(entity_id):
            raise ValueError(f"{entity_id} not found")



# ═══════════════════════════════════════════════
# LAYER 3: INTERFACE ADAPTERS
# ═══════════════════════════════════════════════

class PermissionCreateValidator(ValidatorPort):
    """Concrete validator."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['resource', 'action', 'role']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors



class PermissionController:
    """REST adapter - maps HTTP to use cases."""
    def __init__(self, create_uc: CreatePermissionUseCase,
                 get_uc: GetPermissionUseCase,
                 list_uc: ListPermissionsUseCase,
                 delete_uc: DeletePermissionUseCase):
        self._create = create_uc
        self._get = get_uc
        self._list = list_uc
        self._delete = delete_uc
    
    def handle(self, action: str, **kwargs) -> dict:
        try:
            if action == "create":
                dto = CreatePermissionDTO(**kwargs.get("data", {}))
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

class InMemoryPermissionRepository(PermissionRepositoryPort):
    """Framework-level persistence."""
    def __init__(self):
        self._store: Dict[int, PermissionEntity] = {}
        self._next_id = 1
    
    def save(self, entity: PermissionEntity) -> PermissionEntity:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[PermissionEntity]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[PermissionEntity]:
        return list(self._store.values())
    
    def update(self, entity: PermissionEntity) -> Optional[PermissionEntity]:
        if entity.id not in self._store:
            return None
        self._store[entity.id] = entity
        return entity
    
    def delete(self, entity_id: int) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False


def create_application() -> PermissionController:
    """Composition root - wire all dependencies."""
    repo = InMemoryPermissionRepository()
    validator = PermissionCreateValidator()
    create_uc = CreatePermissionUseCase(repo, validator)
    get_uc = GetPermissionUseCase(repo)
    list_uc = ListPermissionsUseCase(repo)
    delete_uc = DeletePermissionUseCase(repo)
    return PermissionController(create_uc, get_uc, list_uc, delete_uc)
