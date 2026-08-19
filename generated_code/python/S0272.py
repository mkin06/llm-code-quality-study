# Generated: rep=2, llm=gpt-4o
"""Notification system - Clean Architecture + SOLID Principles."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# ═══════════════════════════════════════════════
# LAYER 1: ENTITIES (Domain Models)
# ═══════════════════════════════════════════════

@dataclass
class NotificationEntity:
    """Core domain entity."""
    id: int
        channel: Any = None
    event_type: Any = None
    message: Any = None
    recipient: Any = None
    status: Any = None


class NotificationRepositoryPort(ABC):
    """Domain port for persistence."""
    
    @abstractmethod
    def save(self, entity: NotificationEntity) -> NotificationEntity:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[NotificationEntity]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[NotificationEntity]:
        pass
    
    @abstractmethod
    def update(self, entity: NotificationEntity) -> Optional[NotificationEntity]:
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
class CreateNotificationDTO:
    """DTO for creation requests."""
        channel: Any = None
    event_type: Any = None
    message: Any = None
    recipient: Any = None
    status: Any = None


@dataclass
class NotificationResponseDTO:
    """DTO for responses."""
    id: int
        channel: Any = None
    event_type: Any = None
    message: Any = None
    recipient: Any = None
    status: Any = None
    
    @classmethod
    def from_entity(cls, entity: NotificationEntity) -> "NotificationResponseDTO":
        return cls(id=entity.id, channel=entity.channel, event_type=entity.event_type, message=entity.message, recipient=entity.recipient, status=entity.status)
    
    def to_dict(self) -> dict:
        return {"id": self.id, "channel": self.channel, "event_type": self.event_type, "message": self.message, "recipient": self.recipient, "status": self.status}


# ═══════════════════════════════════════════════
# LAYER 2: USE CASES
# ═══════════════════════════════════════════════

class CreateNotificationUseCase:
    """SRP: only handles creation."""
    def __init__(self, repo: NotificationRepositoryPort, validator: ValidatorPort):
        self._repo = repo
        self._validator = validator
    
    def execute(self, dto: CreateNotificationDTO) -> NotificationResponseDTO:
        errors = self._validator.validate({
            "channel": dto.channel, "event_type": dto.event_type, "message": dto.message, "recipient": dto.recipient, "status": dto.status
        })
        if errors:
            raise ValueError("; ".join(errors))
        entity = NotificationEntity(id=0, channel=dto.channel, event_type=dto.event_type, message=dto.message, recipient=dto.recipient, status=dto.status)
        saved = self._repo.save(entity)
        return NotificationResponseDTO.from_entity(saved)


class GetNotificationUseCase:
    """SRP: only handles retrieval."""
    def __init__(self, repo: NotificationRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> NotificationResponseDTO:
        entity = self._repo.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return NotificationResponseDTO.from_entity(entity)


class ListNotificationsUseCase:
    """SRP: only handles listing."""
    def __init__(self, repo: NotificationRepositoryPort):
        self._repo = repo
    
    def execute(self) -> List[NotificationResponseDTO]:
        return [NotificationResponseDTO.from_entity(e) for e in self._repo.find_all()]


class DeleteNotificationUseCase:
    """SRP: only handles deletion."""
    def __init__(self, repo: NotificationRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> None:
        if not self._repo.delete(entity_id):
            raise ValueError(f"{entity_id} not found")



# ═══════════════════════════════════════════════
# LAYER 3: INTERFACE ADAPTERS
# ═══════════════════════════════════════════════

class NotificationCreateValidator(ValidatorPort):
    """Concrete validator."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['channel', 'event_type', 'message']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors



class NotificationController:
    """REST adapter - maps HTTP to use cases."""
    def __init__(self, create_uc: CreateNotificationUseCase,
                 get_uc: GetNotificationUseCase,
                 list_uc: ListNotificationsUseCase,
                 delete_uc: DeleteNotificationUseCase):
        self._create = create_uc
        self._get = get_uc
        self._list = list_uc
        self._delete = delete_uc
    
    def handle(self, action: str, **kwargs) -> dict:
        try:
            if action == "create":
                dto = CreateNotificationDTO(**kwargs.get("data", {}))
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

class InMemoryNotificationRepository(NotificationRepositoryPort):
    """Framework-level persistence."""
    def __init__(self):
        self._store: Dict[int, NotificationEntity] = {}
        self._next_id = 1
    
    def save(self, entity: NotificationEntity) -> NotificationEntity:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[NotificationEntity]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[NotificationEntity]:
        return list(self._store.values())
    
    def update(self, entity: NotificationEntity) -> Optional[NotificationEntity]:
        if entity.id not in self._store:
            return None
        self._store[entity.id] = entity
        return entity
    
    def delete(self, entity_id: int) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False


def create_application() -> NotificationController:
    """Composition root - wire all dependencies."""
    repo = InMemoryNotificationRepository()
    validator = NotificationCreateValidator()
    create_uc = CreateNotificationUseCase(repo, validator)
    get_uc = GetNotificationUseCase(repo)
    list_uc = ListNotificationsUseCase(repo)
    delete_uc = DeleteNotificationUseCase(repo)
    return NotificationController(create_uc, get_uc, list_uc, delete_uc)
