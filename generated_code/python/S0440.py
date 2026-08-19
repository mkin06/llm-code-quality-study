# Generated: rep=5, llm=claude-3.5-sonnet
"""Task scheduler - Clean Architecture + SOLID Principles."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# ═══════════════════════════════════════════════
# LAYER 1: ENTITIES (Domain Models)
# ═══════════════════════════════════════════════

@dataclass
class TaskEntity:
    """Core domain entity."""
    id: int
        name: Any = None
    priority: Any = None
    scheduled_time: Any = None
    status: Any = None
    max_retries: Any = None


class TaskRepositoryPort(ABC):
    """Domain port for persistence."""
    
    @abstractmethod
    def save(self, entity: TaskEntity) -> TaskEntity:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[TaskEntity]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[TaskEntity]:
        pass
    
    @abstractmethod
    def update(self, entity: TaskEntity) -> Optional[TaskEntity]:
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
class CreateTaskDTO:
    """DTO for creation requests."""
        name: Any = None
    priority: Any = None
    scheduled_time: Any = None
    status: Any = None
    max_retries: Any = None


@dataclass
class TaskResponseDTO:
    """DTO for responses."""
    id: int
        name: Any = None
    priority: Any = None
    scheduled_time: Any = None
    status: Any = None
    max_retries: Any = None
    
    @classmethod
    def from_entity(cls, entity: TaskEntity) -> "TaskResponseDTO":
        return cls(id=entity.id, name=entity.name, priority=entity.priority, scheduled_time=entity.scheduled_time, status=entity.status, max_retries=entity.max_retries)
    
    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "priority": self.priority, "scheduled_time": self.scheduled_time, "status": self.status, "max_retries": self.max_retries}


# ═══════════════════════════════════════════════
# LAYER 2: USE CASES
# ═══════════════════════════════════════════════

class CreateTaskUseCase:
    """SRP: only handles creation."""
    def __init__(self, repo: TaskRepositoryPort, validator: ValidatorPort):
        self._repo = repo
        self._validator = validator
    
    def execute(self, dto: CreateTaskDTO) -> TaskResponseDTO:
        errors = self._validator.validate({
            "name": dto.name, "priority": dto.priority, "scheduled_time": dto.scheduled_time, "status": dto.status, "max_retries": dto.max_retries
        })
        if errors:
            raise ValueError("; ".join(errors))
        entity = TaskEntity(id=0, name=dto.name, priority=dto.priority, scheduled_time=dto.scheduled_time, status=dto.status, max_retries=dto.max_retries)
        saved = self._repo.save(entity)
        return TaskResponseDTO.from_entity(saved)


class GetTaskUseCase:
    """SRP: only handles retrieval."""
    def __init__(self, repo: TaskRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> TaskResponseDTO:
        entity = self._repo.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return TaskResponseDTO.from_entity(entity)


class ListTasksUseCase:
    """SRP: only handles listing."""
    def __init__(self, repo: TaskRepositoryPort):
        self._repo = repo
    
    def execute(self) -> List[TaskResponseDTO]:
        return [TaskResponseDTO.from_entity(e) for e in self._repo.find_all()]


class DeleteTaskUseCase:
    """SRP: only handles deletion."""
    def __init__(self, repo: TaskRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> None:
        if not self._repo.delete(entity_id):
            raise ValueError(f"{entity_id} not found")



# ═══════════════════════════════════════════════
# LAYER 3: INTERFACE ADAPTERS
# ═══════════════════════════════════════════════

class TaskCreateValidator(ValidatorPort):
    """Concrete validator."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['name', 'priority', 'scheduled_time']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors



class TaskController:
    """REST adapter - maps HTTP to use cases."""
    def __init__(self, create_uc: CreateTaskUseCase,
                 get_uc: GetTaskUseCase,
                 list_uc: ListTasksUseCase,
                 delete_uc: DeleteTaskUseCase):
        self._create = create_uc
        self._get = get_uc
        self._list = list_uc
        self._delete = delete_uc
    
    def handle(self, action: str, **kwargs) -> dict:
        try:
            if action == "create":
                dto = CreateTaskDTO(**kwargs.get("data", {}))
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

class InMemoryTaskRepository(TaskRepositoryPort):
    """Framework-level persistence."""
    def __init__(self):
        self._store: Dict[int, TaskEntity] = {}
        self._next_id = 1
    
    def save(self, entity: TaskEntity) -> TaskEntity:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[TaskEntity]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[TaskEntity]:
        return list(self._store.values())
    
    def update(self, entity: TaskEntity) -> Optional[TaskEntity]:
        if entity.id not in self._store:
            return None
        self._store[entity.id] = entity
        return entity
    
    def delete(self, entity_id: int) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False


def create_application() -> TaskController:
    """Composition root - wire all dependencies."""
    repo = InMemoryTaskRepository()
    validator = TaskCreateValidator()
    create_uc = CreateTaskUseCase(repo, validator)
    get_uc = GetTaskUseCase(repo)
    list_uc = ListTasksUseCase(repo)
    delete_uc = DeleteTaskUseCase(repo)
    return TaskController(create_uc, get_uc, list_uc, delete_uc)
