# Generated: rep=2, llm=gpt-4o
"""Data pipeline - Design Patterns + Dependency Injection."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class PipelineRecord:
    """Domain entity."""
    def __init__(self, entity_id: int, data: Any = None, stage: Any = None, status: Any = None, errors: Any = None):
        self.id = entity_id
                self.data = data
        self.stage = stage
        self.status = status
        self.errors = errors
    
    def to_dict(self) -> dict:
        return {"id": self.id, "data": self.data, "stage": self.stage, "status": self.status, "errors": self.errors}


class PipelineRecordRepositoryInterface(ABC):
    """Abstract repository for pipelinerecord persistence."""
    
    @abstractmethod
    def save(self, entity: PipelineRecord) -> PipelineRecord:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[PipelineRecord]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[PipelineRecord]:
        pass
    
    @abstractmethod
    def update(self, entity: PipelineRecord) -> Optional[PipelineRecord]:
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass


class InMemoryPipelineRecordRepository(PipelineRecordRepositoryInterface):
    """In-memory implementation of repository."""
    
    def __init__(self):
        self._store: Dict[int, PipelineRecord] = {}
        self._next_id = 1
    
    def save(self, entity: PipelineRecord) -> PipelineRecord:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[PipelineRecord]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[PipelineRecord]:
        return list(self._store.values())
    
    def update(self, entity: PipelineRecord) -> Optional[PipelineRecord]:
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


class PipelineRecordCreateValidator(ValidationStrategy):
    """Validates creation data."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['data', 'stage', 'status', 'errors']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors








class PipelineRecordService:
    """Business logic with dependency injection."""
    
    def __init__(self, repository: PipelineRecordRepositoryInterface,
                 validator: ValidationStrategy):
        self._repository = repository
        self._validator = validator
    
    def create(self, data: dict) -> PipelineRecord:
        errors = self._validator.validate(data)
        if errors:
            raise ValueError("; ".join(errors))
        entity = PipelineRecord(entity_id=0, **{k: data.get(k) for k in ['data', 'stage', 'status', 'errors']})
        return self._repository.save(entity)
    
    def get(self, entity_id: int) -> PipelineRecord:
        entity = self._repository.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return entity
    
    def list_all(self) -> List[PipelineRecord]:
        return self._repository.find_all()
    
    def delete(self, entity_id: int) -> None:
        if not self._repository.delete(entity_id):
            raise ValueError(f"{entity_id} not found")


class PipelineRecordController:
    """Controller with injected service."""
    
    def __init__(self, service: PipelineRecordService):
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


def create_application() -> PipelineRecordController:
    """Wire dependencies."""
    repo = InMemoryPipelineRecordRepository()
    validator = PipelineRecordCreateValidator()
    service = PipelineRecordService(repo, validator)
    return PipelineRecordController(service)
