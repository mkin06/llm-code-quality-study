# Generated: rep=2, llm=claude-3.5-sonnet
"""Data pipeline - Clean Architecture + SOLID Principles."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# ═══════════════════════════════════════════════
# LAYER 1: ENTITIES (Domain Models)
# ═══════════════════════════════════════════════

@dataclass
class PipelineRecordEntity:
    """Core domain entity."""
    id: int
        data: Any = None
    stage: Any = None
    status: Any = None
    errors: Any = None


class PipelineRecordRepositoryPort(ABC):
    """Domain port for persistence."""
    
    @abstractmethod
    def save(self, entity: PipelineRecordEntity) -> PipelineRecordEntity:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[PipelineRecordEntity]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[PipelineRecordEntity]:
        pass
    
    @abstractmethod
    def update(self, entity: PipelineRecordEntity) -> Optional[PipelineRecordEntity]:
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
class CreatePipelineRecordDTO:
    """DTO for creation requests."""
        data: Any = None
    stage: Any = None
    status: Any = None
    errors: Any = None


@dataclass
class PipelineRecordResponseDTO:
    """DTO for responses."""
    id: int
        data: Any = None
    stage: Any = None
    status: Any = None
    errors: Any = None
    
    @classmethod
    def from_entity(cls, entity: PipelineRecordEntity) -> "PipelineRecordResponseDTO":
        return cls(id=entity.id, data=entity.data, stage=entity.stage, status=entity.status, errors=entity.errors)
    
    def to_dict(self) -> dict:
        return {"id": self.id, "data": self.data, "stage": self.stage, "status": self.status, "errors": self.errors}


# ═══════════════════════════════════════════════
# LAYER 2: USE CASES
# ═══════════════════════════════════════════════

class CreatePipelineRecordUseCase:
    """SRP: only handles creation."""
    def __init__(self, repo: PipelineRecordRepositoryPort, validator: ValidatorPort):
        self._repo = repo
        self._validator = validator
    
    def execute(self, dto: CreatePipelineRecordDTO) -> PipelineRecordResponseDTO:
        errors = self._validator.validate({
            "data": dto.data, "stage": dto.stage, "status": dto.status, "errors": dto.errors
        })
        if errors:
            raise ValueError("; ".join(errors))
        entity = PipelineRecordEntity(id=0, data=dto.data, stage=dto.stage, status=dto.status, errors=dto.errors)
        saved = self._repo.save(entity)
        return PipelineRecordResponseDTO.from_entity(saved)


class GetPipelineRecordUseCase:
    """SRP: only handles retrieval."""
    def __init__(self, repo: PipelineRecordRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> PipelineRecordResponseDTO:
        entity = self._repo.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return PipelineRecordResponseDTO.from_entity(entity)


class ListPipelineRecordsUseCase:
    """SRP: only handles listing."""
    def __init__(self, repo: PipelineRecordRepositoryPort):
        self._repo = repo
    
    def execute(self) -> List[PipelineRecordResponseDTO]:
        return [PipelineRecordResponseDTO.from_entity(e) for e in self._repo.find_all()]


class DeletePipelineRecordUseCase:
    """SRP: only handles deletion."""
    def __init__(self, repo: PipelineRecordRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> None:
        if not self._repo.delete(entity_id):
            raise ValueError(f"{entity_id} not found")



# ═══════════════════════════════════════════════
# LAYER 3: INTERFACE ADAPTERS
# ═══════════════════════════════════════════════

class PipelineRecordCreateValidator(ValidatorPort):
    """Concrete validator."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['data', 'stage', 'status']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors



class PipelineRecordController:
    """REST adapter - maps HTTP to use cases."""
    def __init__(self, create_uc: CreatePipelineRecordUseCase,
                 get_uc: GetPipelineRecordUseCase,
                 list_uc: ListPipelineRecordsUseCase,
                 delete_uc: DeletePipelineRecordUseCase):
        self._create = create_uc
        self._get = get_uc
        self._list = list_uc
        self._delete = delete_uc
    
    def handle(self, action: str, **kwargs) -> dict:
        try:
            if action == "create":
                dto = CreatePipelineRecordDTO(**kwargs.get("data", {}))
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

class InMemoryPipelineRecordRepository(PipelineRecordRepositoryPort):
    """Framework-level persistence."""
    def __init__(self):
        self._store: Dict[int, PipelineRecordEntity] = {}
        self._next_id = 1
    
    def save(self, entity: PipelineRecordEntity) -> PipelineRecordEntity:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[PipelineRecordEntity]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[PipelineRecordEntity]:
        return list(self._store.values())
    
    def update(self, entity: PipelineRecordEntity) -> Optional[PipelineRecordEntity]:
        if entity.id not in self._store:
            return None
        self._store[entity.id] = entity
        return entity
    
    def delete(self, entity_id: int) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False


def create_application() -> PipelineRecordController:
    """Composition root - wire all dependencies."""
    repo = InMemoryPipelineRecordRepository()
    validator = PipelineRecordCreateValidator()
    create_uc = CreatePipelineRecordUseCase(repo, validator)
    get_uc = GetPipelineRecordUseCase(repo)
    list_uc = ListPipelineRecordsUseCase(repo)
    delete_uc = DeletePipelineRecordUseCase(repo)
    return PipelineRecordController(create_uc, get_uc, list_uc, delete_uc)
