# Generated: rep=5, llm=gpt-4o
"""Task scheduler - Design Patterns + Dependency Injection."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class Task:
    """Domain entity."""
    def __init__(self, entity_id: int, name: Any = None, priority: Any = None, scheduled_time: Any = None, status: Any = None, max_retries: Any = None):
        self.id = entity_id
                self.name = name
        self.priority = priority
        self.scheduled_time = scheduled_time
        self.status = status
        self.max_retries = max_retries
    
    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "priority": self.priority, "scheduled_time": self.scheduled_time, "status": self.status, "max_retries": self.max_retries}


class TaskRepositoryInterface(ABC):
    """Abstract repository for task persistence."""
    
    @abstractmethod
    def save(self, entity: Task) -> Task:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[Task]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Task]:
        pass
    
    @abstractmethod
    def update(self, entity: Task) -> Optional[Task]:
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass


class InMemoryTaskRepository(TaskRepositoryInterface):
    """In-memory implementation of repository."""
    
    def __init__(self):
        self._store: Dict[int, Task] = {}
        self._next_id = 1
    
    def save(self, entity: Task) -> Task:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[Task]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[Task]:
        return list(self._store.values())
    
    def update(self, entity: Task) -> Optional[Task]:
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


class TaskCreateValidator(ValidationStrategy):
    """Validates creation data."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['name', 'priority', 'scheduled_time', 'status', 'max_retries']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors








class TaskService:
    """Business logic with dependency injection."""
    
    def __init__(self, repository: TaskRepositoryInterface,
                 validator: ValidationStrategy):
        self._repository = repository
        self._validator = validator
    
    def create(self, data: dict) -> Task:
        errors = self._validator.validate(data)
        if errors:
            raise ValueError("; ".join(errors))
        entity = Task(entity_id=0, **{k: data.get(k) for k in ['name', 'priority', 'scheduled_time', 'status', 'max_retries']})
        return self._repository.save(entity)
    
    def get(self, entity_id: int) -> Task:
        entity = self._repository.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return entity
    
    def list_all(self) -> List[Task]:
        return self._repository.find_all()
    
    def delete(self, entity_id: int) -> None:
        if not self._repository.delete(entity_id):
            raise ValueError(f"{entity_id} not found")


class TaskController:
    """Controller with injected service."""
    
    def __init__(self, service: TaskService):
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


def create_application() -> TaskController:
    """Wire dependencies."""
    repo = InMemoryTaskRepository()
    validator = TaskCreateValidator()
    service = TaskService(repo, validator)
    return TaskController(service)
