# Generated: rep=4, llm=claude-3.5-sonnet
"""Event bus - Clean Architecture + SOLID Principles."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# ═══════════════════════════════════════════════
# LAYER 1: ENTITIES (Domain Models)
# ═══════════════════════════════════════════════

@dataclass
class EventEntity:
    """Core domain entity."""
    id: int
        event_type: Any = None
    payload: Any = None
    timestamp: Any = None
    source: Any = None


class EventRepositoryPort(ABC):
    """Domain port for persistence."""
    
    @abstractmethod
    def save(self, entity: EventEntity) -> EventEntity:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[EventEntity]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[EventEntity]:
        pass
    
    @abstractmethod
    def update(self, entity: EventEntity) -> Optional[EventEntity]:
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
class CreateEventDTO:
    """DTO for creation requests."""
        event_type: Any = None
    payload: Any = None
    timestamp: Any = None
    source: Any = None


@dataclass
class EventResponseDTO:
    """DTO for responses."""
    id: int
        event_type: Any = None
    payload: Any = None
    timestamp: Any = None
    source: Any = None
    
    @classmethod
    def from_entity(cls, entity: EventEntity) -> "EventResponseDTO":
        return cls(id=entity.id, event_type=entity.event_type, payload=entity.payload, timestamp=entity.timestamp, source=entity.source)
    
    def to_dict(self) -> dict:
        return {"id": self.id, "event_type": self.event_type, "payload": self.payload, "timestamp": self.timestamp, "source": self.source}


# ═══════════════════════════════════════════════
# LAYER 2: USE CASES
# ═══════════════════════════════════════════════

class CreateEventUseCase:
    """SRP: only handles creation."""
    def __init__(self, repo: EventRepositoryPort, validator: ValidatorPort):
        self._repo = repo
        self._validator = validator
    
    def execute(self, dto: CreateEventDTO) -> EventResponseDTO:
        errors = self._validator.validate({
            "event_type": dto.event_type, "payload": dto.payload, "timestamp": dto.timestamp, "source": dto.source
        })
        if errors:
            raise ValueError("; ".join(errors))
        entity = EventEntity(id=0, event_type=dto.event_type, payload=dto.payload, timestamp=dto.timestamp, source=dto.source)
        saved = self._repo.save(entity)
        return EventResponseDTO.from_entity(saved)


class GetEventUseCase:
    """SRP: only handles retrieval."""
    def __init__(self, repo: EventRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> EventResponseDTO:
        entity = self._repo.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return EventResponseDTO.from_entity(entity)


class ListEventsUseCase:
    """SRP: only handles listing."""
    def __init__(self, repo: EventRepositoryPort):
        self._repo = repo
    
    def execute(self) -> List[EventResponseDTO]:
        return [EventResponseDTO.from_entity(e) for e in self._repo.find_all()]


class DeleteEventUseCase:
    """SRP: only handles deletion."""
    def __init__(self, repo: EventRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> None:
        if not self._repo.delete(entity_id):
            raise ValueError(f"{entity_id} not found")



# ═══════════════════════════════════════════════
# LAYER 3: INTERFACE ADAPTERS
# ═══════════════════════════════════════════════

class EventCreateValidator(ValidatorPort):
    """Concrete validator."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['event_type', 'payload', 'timestamp']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors



class EventController:
    """REST adapter - maps HTTP to use cases."""
    def __init__(self, create_uc: CreateEventUseCase,
                 get_uc: GetEventUseCase,
                 list_uc: ListEventsUseCase,
                 delete_uc: DeleteEventUseCase):
        self._create = create_uc
        self._get = get_uc
        self._list = list_uc
        self._delete = delete_uc
    
    def handle(self, action: str, **kwargs) -> dict:
        try:
            if action == "create":
                dto = CreateEventDTO(**kwargs.get("data", {}))
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

class InMemoryEventRepository(EventRepositoryPort):
    """Framework-level persistence."""
    def __init__(self):
        self._store: Dict[int, EventEntity] = {}
        self._next_id = 1
    
    def save(self, entity: EventEntity) -> EventEntity:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[EventEntity]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[EventEntity]:
        return list(self._store.values())
    
    def update(self, entity: EventEntity) -> Optional[EventEntity]:
        if entity.id not in self._store:
            return None
        self._store[entity.id] = entity
        return entity
    
    def delete(self, entity_id: int) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False


def create_application() -> EventController:
    """Composition root - wire all dependencies."""
    repo = InMemoryEventRepository()
    validator = EventCreateValidator()
    create_uc = CreateEventUseCase(repo, validator)
    get_uc = GetEventUseCase(repo)
    list_uc = ListEventsUseCase(repo)
    delete_uc = DeleteEventUseCase(repo)
    return EventController(create_uc, get_uc, list_uc, delete_uc)
