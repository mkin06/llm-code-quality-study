# Generated: rep=2, llm=claude-3.5-sonnet
"""Event bus - Design Patterns + Dependency Injection."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class Event:
    """Domain entity."""
    def __init__(self, entity_id: int, event_type: Any = None, payload: Any = None, timestamp: Any = None, source: Any = None):
        self.id = entity_id
                self.event_type = event_type
        self.payload = payload
        self.timestamp = timestamp
        self.source = source
    
    def to_dict(self) -> dict:
        return {"id": self.id, "event_type": self.event_type, "payload": self.payload, "timestamp": self.timestamp, "source": self.source}


class EventRepositoryInterface(ABC):
    """Abstract repository for event persistence."""
    
    @abstractmethod
    def save(self, entity: Event) -> Event:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[Event]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Event]:
        pass
    
    @abstractmethod
    def update(self, entity: Event) -> Optional[Event]:
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass


class InMemoryEventRepository(EventRepositoryInterface):
    """In-memory implementation of repository."""
    
    def __init__(self):
        self._store: Dict[int, Event] = {}
        self._next_id = 1
    
    def save(self, entity: Event) -> Event:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[Event]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[Event]:
        return list(self._store.values())
    
    def update(self, entity: Event) -> Optional[Event]:
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


class EventCreateValidator(ValidationStrategy):
    """Validates creation data."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['event_type', 'payload', 'timestamp', 'source']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors








class EventService:
    """Business logic with dependency injection."""
    
    def __init__(self, repository: EventRepositoryInterface,
                 validator: ValidationStrategy):
        self._repository = repository
        self._validator = validator
    
    def create(self, data: dict) -> Event:
        errors = self._validator.validate(data)
        if errors:
            raise ValueError("; ".join(errors))
        entity = Event(entity_id=0, **{k: data.get(k) for k in ['event_type', 'payload', 'timestamp', 'source']})
        return self._repository.save(entity)
    
    def get(self, entity_id: int) -> Event:
        entity = self._repository.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return entity
    
    def list_all(self) -> List[Event]:
        return self._repository.find_all()
    
    def delete(self, entity_id: int) -> None:
        if not self._repository.delete(entity_id):
            raise ValueError(f"{entity_id} not found")


class EventController:
    """Controller with injected service."""
    
    def __init__(self, service: EventService):
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


def create_application() -> EventController:
    """Wire dependencies."""
    repo = InMemoryEventRepository()
    validator = EventCreateValidator()
    service = EventService(repo, validator)
    return EventController(service)
