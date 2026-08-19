# Generated: rep=3, llm=claude-3.5-sonnet
"""File management system - Clean Architecture + SOLID Principles."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# ═══════════════════════════════════════════════
# LAYER 1: ENTITIES (Domain Models)
# ═══════════════════════════════════════════════

@dataclass
class FileRecordEntity:
    """Core domain entity."""
    id: int
        filename: Any = None
    size_bytes: Any = None
    mime_type: Any = None
    upload_date: Any = None
    checksum: Any = None


class FileRecordRepositoryPort(ABC):
    """Domain port for persistence."""
    
    @abstractmethod
    def save(self, entity: FileRecordEntity) -> FileRecordEntity:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[FileRecordEntity]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[FileRecordEntity]:
        pass
    
    @abstractmethod
    def update(self, entity: FileRecordEntity) -> Optional[FileRecordEntity]:
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
class CreateFileRecordDTO:
    """DTO for creation requests."""
        filename: Any = None
    size_bytes: Any = None
    mime_type: Any = None
    upload_date: Any = None
    checksum: Any = None


@dataclass
class FileRecordResponseDTO:
    """DTO for responses."""
    id: int
        filename: Any = None
    size_bytes: Any = None
    mime_type: Any = None
    upload_date: Any = None
    checksum: Any = None
    
    @classmethod
    def from_entity(cls, entity: FileRecordEntity) -> "FileRecordResponseDTO":
        return cls(id=entity.id, filename=entity.filename, size_bytes=entity.size_bytes, mime_type=entity.mime_type, upload_date=entity.upload_date, checksum=entity.checksum)
    
    def to_dict(self) -> dict:
        return {"id": self.id, "filename": self.filename, "size_bytes": self.size_bytes, "mime_type": self.mime_type, "upload_date": self.upload_date, "checksum": self.checksum}


# ═══════════════════════════════════════════════
# LAYER 2: USE CASES
# ═══════════════════════════════════════════════

class CreateFileRecordUseCase:
    """SRP: only handles creation."""
    def __init__(self, repo: FileRecordRepositoryPort, validator: ValidatorPort):
        self._repo = repo
        self._validator = validator
    
    def execute(self, dto: CreateFileRecordDTO) -> FileRecordResponseDTO:
        errors = self._validator.validate({
            "filename": dto.filename, "size_bytes": dto.size_bytes, "mime_type": dto.mime_type, "upload_date": dto.upload_date, "checksum": dto.checksum
        })
        if errors:
            raise ValueError("; ".join(errors))
        entity = FileRecordEntity(id=0, filename=dto.filename, size_bytes=dto.size_bytes, mime_type=dto.mime_type, upload_date=dto.upload_date, checksum=dto.checksum)
        saved = self._repo.save(entity)
        return FileRecordResponseDTO.from_entity(saved)


class GetFileRecordUseCase:
    """SRP: only handles retrieval."""
    def __init__(self, repo: FileRecordRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> FileRecordResponseDTO:
        entity = self._repo.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{entity_id} not found")
        return FileRecordResponseDTO.from_entity(entity)


class ListFileRecordsUseCase:
    """SRP: only handles listing."""
    def __init__(self, repo: FileRecordRepositoryPort):
        self._repo = repo
    
    def execute(self) -> List[FileRecordResponseDTO]:
        return [FileRecordResponseDTO.from_entity(e) for e in self._repo.find_all()]


class DeleteFileRecordUseCase:
    """SRP: only handles deletion."""
    def __init__(self, repo: FileRecordRepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> None:
        if not self._repo.delete(entity_id):
            raise ValueError(f"{entity_id} not found")



# ═══════════════════════════════════════════════
# LAYER 3: INTERFACE ADAPTERS
# ═══════════════════════════════════════════════

class FileRecordCreateValidator(ValidatorPort):
    """Concrete validator."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in ['filename', 'size_bytes', 'mime_type']:
            if not data.get(field):
                errors.append(f"{field} is required")
        return errors



class FileRecordController:
    """REST adapter - maps HTTP to use cases."""
    def __init__(self, create_uc: CreateFileRecordUseCase,
                 get_uc: GetFileRecordUseCase,
                 list_uc: ListFileRecordsUseCase,
                 delete_uc: DeleteFileRecordUseCase):
        self._create = create_uc
        self._get = get_uc
        self._list = list_uc
        self._delete = delete_uc
    
    def handle(self, action: str, **kwargs) -> dict:
        try:
            if action == "create":
                dto = CreateFileRecordDTO(**kwargs.get("data", {}))
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

class InMemoryFileRecordRepository(FileRecordRepositoryPort):
    """Framework-level persistence."""
    def __init__(self):
        self._store: Dict[int, FileRecordEntity] = {}
        self._next_id = 1
    
    def save(self, entity: FileRecordEntity) -> FileRecordEntity:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[FileRecordEntity]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[FileRecordEntity]:
        return list(self._store.values())
    
    def update(self, entity: FileRecordEntity) -> Optional[FileRecordEntity]:
        if entity.id not in self._store:
            return None
        self._store[entity.id] = entity
        return entity
    
    def delete(self, entity_id: int) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False


def create_application() -> FileRecordController:
    """Composition root - wire all dependencies."""
    repo = InMemoryFileRecordRepository()
    validator = FileRecordCreateValidator()
    create_uc = CreateFileRecordUseCase(repo, validator)
    get_uc = GetFileRecordUseCase(repo)
    list_uc = ListFileRecordsUseCase(repo)
    delete_uc = DeleteFileRecordUseCase(repo)
    return FileRecordController(create_uc, get_uc, list_uc, delete_uc)
