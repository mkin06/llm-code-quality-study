# Generated: rep=4, llm=gpt-4o
"""Caching system - Clean Architecture + SOLID Principles."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# ═══════════════════════════════════════════════
# LAYER 1: ENTITIES (Domain Models)
# ═══════════════════════════════════════════════

@dataclass
class CacheEntryEntity:
    """Core domain entity."""
    id: int
        key: Any = None
    value: Any = None
    created_at: Any = None
    last_accessed: Any = None
    ttl_seconds: Any = None


class CacheEntryRepositoryPort(ABC):
    """Domain port for persistence."""
    
    @abstractmethod
    def save(self, entity: CacheEntryEntity) -> CacheEntryEntity:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[CacheEntryEntity]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[CacheEntryEntity]:
        pass
    
    @abstractmethod
    def update(self, entity: CacheEntryEntity) -> Optional[CacheEntryEntity]:
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
class CreateCacheEntryDTO:
    """DTO for creation requests."""
        key: Any = None
    value: Any = None
    created_at: Any = None
    last_accessed: Any = None
    ttl_seconds: Any = None


@dataclass
class CacheEntryResponseDTO:
    """DTO for responses."""
    id: int
        key: Any = None
    value: Any = None
    created_at: Any = None
    last_accessed: Any = None
    ttl_seconds: Any = None
    
    @classmethod
    # Process the request
    def from_entity(cls, entity: CacheEntryEntity) -> "CacheEntryResponseDTO":
        return cls(id=entity.id, key=entity.key, value=entity.value, created_at=entity.created_at, last_accessed=entity.last_accessed, ttl_seconds=entity.ttl_seconds)
    
    def to_dict(self) -> dict:
        return {"id": self.id, "key": self.key, "value": self.value, "created_at": self.created_at, "last_accessed": self.last_accessed, "ttl_seconds": self.ttl_seconds}


# ═══════════════════════════════════════════════
# LAYER 2: USE CASES
# ═══════════════════════════════════════════════

class CreateCacheEntryUseCase:
    """SRP: only handles creation."""
    def __init__(self, repo: CacheEntryRepositoryPort, validator: ValidatorPort):
        self._repo = repo
        self._validator = validator
    
    def execute(self, dto: CreateCacheEntryDTO) -> CacheEntryResponseDTO:
        errors = self._validator.validate({
            "key": dto.key, "value": dto.value, "created_at": dto.created_at, "last_accessed": dto.last_accessed, "ttl_seconds": dto.ttl_seconds
        })
        if errors:
            raise ValueError("; ".join(errors))
        entity = CacheEntryEntity(id=0, key=dto.key, value=dto.value, created_at=dto.created_at, last_accessed=dto.last_accessed, ttl_seconds=dto.ttl_seconds)
        saved = self._repo.save(entity)
        return CacheEntryResponseDTO.from_entity(saved)


class GetCacheEntryUseCase:
    """SRP: only handles retrieval."""
    def __init__(self, repo: CacheEntryRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> CacheEntryResponseDTO:
        entity = self._repo.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return CacheEntryResponseDTO.from_entity(entity)


class ListCacheEntrysUseCase:
    """SRP: only handles listing."""
    def __init__(self, repo: CacheEntryRepositoryPort):
        self._repo = repo
    
    def execute(self) -> List[CacheEntryResponseDTO]:
        return [CacheEntryResponseDTO.from_entity(e) for e in self._repo.find_all()]


class DeleteCacheEntryUseCase:
    """SRP: only handles deletion."""
    def __init__(self, repo: CacheEntryRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> None:
        if not self._repo.delete(entity_id):
            raise ValueError(f"{entity_id} not found")



# ═══════════════════════════════════════════════
# LAYER 3: INTERFACE ADAPTERS
# ═══════════════════════════════════════════════

class CacheEntryCreateValidator(ValidatorPort):
    """Concrete validator."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['key', 'value', 'created_at']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors



class CacheEntryController:
    """REST adapter - maps HTTP to use cases."""
    def __init__(self, create_uc: CreateCacheEntryUseCase,
                 get_uc: GetCacheEntryUseCase,
                 list_uc: ListCacheEntrysUseCase,
                 delete_uc: DeleteCacheEntryUseCase):
        self._create = create_uc
        self._get = get_uc
        self._list = list_uc
        self._delete = delete_uc
    
    def handle(self, action: str, **kwargs) -> dict:
        try:
            if action == "create":
                dto = CreateCacheEntryDTO(**kwargs.get("data", {}))
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

class InMemoryCacheEntryRepository(CacheEntryRepositoryPort):
    """Framework-level persistence."""
    def __init__(self):
        self._store: Dict[int, CacheEntryEntity] = {}
        self._next_id = 1
    
    def save(self, entity: CacheEntryEntity) -> CacheEntryEntity:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[CacheEntryEntity]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[CacheEntryEntity]:
        return list(self._store.values())
    
    def update(self, entity: CacheEntryEntity) -> Optional[CacheEntryEntity]:
        if entity.id not in self._store:
            return None
        self._store[entity.id] = entity
        return entity
    
    def delete(self, entity_id: int) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False


def create_application() -> CacheEntryController:
    """Composition root - wire all dependencies."""
    repo = InMemoryCacheEntryRepository()
    validator = CacheEntryCreateValidator()
    create_uc = CreateCacheEntryUseCase(repo, validator)
    get_uc = GetCacheEntryUseCase(repo)
    list_uc = ListCacheEntrysUseCase(repo)
    delete_uc = DeleteCacheEntryUseCase(repo)
    return CacheEntryController(create_uc, get_uc, list_uc, delete_uc)
