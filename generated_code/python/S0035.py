# Generated: rep=5, llm=gpt-4o
"""CRUD REST API - Clean Architecture + SOLID Principles."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# LAYER 1: ENTITIES (Domain Models)
# ═══════════════════════════════════════════════════════════════

@dataclass
class Book:
    """Core domain entity for a book."""
    id: int
    title: str
    author: str
    isbn: str
    published_year: Optional[int] = None
    genre: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# LAYER 1: ENTITY INTERFACES (Domain Contracts)
# ═══════════════════════════════════════════════════════════════

class BookRepositoryPort(ABC):
    """Port for book persistence - defined in domain layer."""
    
    @abstractmethod
    def save(self, book: Book) -> Book:
        pass
    
    @abstractmethod
    def find_by_id(self, book_id: int) -> Optional[Book]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Book]:
        pass
    
    @abstractmethod
    def update(self, book: Book) -> Optional[Book]:
        pass
    
    @abstractmethod
    def delete(self, book_id: int) -> bool:
        pass


class ValidatorPort(ABC):
    """Port for data validation."""
    
    @abstractmethod
    def validate(self, data: dict) -> List[str]:
        pass


# ═══════════════════════════════════════════════════════════════
# DTOs (Data Transfer Objects)
# ═══════════════════════════════════════════════════════════════

@dataclass
class CreateBookDTO:
    """DTO for book creation requests."""
    title: str
    author: str
    isbn: str
    published_year: Optional[int] = None
    genre: Optional[str] = None


@dataclass
class UpdateBookDTO:
    """DTO for book update requests."""
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    published_year: Optional[int] = None
    genre: Optional[str] = None


@dataclass
class BookResponseDTO:
    """DTO for book response data."""
    id: int
    title: str
    author: str
    isbn: str
    published_year: Optional[int]
    genre: Optional[str]
    
    @classmethod
    def from_entity(cls, book: Book) -> "BookResponseDTO":
        return cls(
            id=book.id, title=book.title, author=book.author,
            isbn=book.isbn, published_year=book.published_year,
            genre=book.genre
        )
    
    def to_dict(self) -> dict:
        return {
            "id": self.id, "title": self.title, "author": self.author,
            "isbn": self.isbn, "published_year": self.published_year,
            "genre": self.genre
        }


# ═══════════════════════════════════════════════════════════════
# LAYER 2: USE CASES (Application Logic)
# ═══════════════════════════════════════════════════════════════

class CreateBookUseCase:
    """SRP: handles only book creation logic."""
    
    def __init__(self, repository: BookRepositoryPort,
                 validator: ValidatorPort):
        self._repository = repository
        self._validator = validator
    
    def execute(self, dto: CreateBookDTO) -> BookResponseDTO:
        errors = self._validator.validate({
            "title": dto.title, "author": dto.author, "isbn": dto.isbn
        })
        if errors:
            raise ValueError("; ".join(errors))
        book = Book(
            id=0, title=dto.title, author=dto.author,
            isbn=dto.isbn, published_year=dto.published_year,
            genre=dto.genre
        )
        saved = self._repository.save(book)
        return BookResponseDTO.from_entity(saved)


class GetBookUseCase:
    """SRP: handles retrieving a single book."""
    
    def __init__(self, repository: BookRepositoryPort):
        self._repository = repository
    
    def execute(self, book_id: int) -> BookResponseDTO:
        book = self._repository.find_by_id(book_id)
        if not book:
            raise ValueError(f"Book {book_id} not found")
        return BookResponseDTO.from_entity(book)


class ListBooksUseCase:
    """SRP: handles listing all books."""
    
    def __init__(self, repository: BookRepositoryPort):
        self._repository = repository
    
    def execute(self) -> List[BookResponseDTO]:
        books = self._repository.find_all()
        return [BookResponseDTO.from_entity(b) for b in books]


class UpdateBookUseCase:
    """SRP: handles book updates."""
    
    def __init__(self, repository: BookRepositoryPort):
        self._repository = repository
    
    def execute(self, book_id: int, dto: UpdateBookDTO) -> BookResponseDTO:
        book = self._repository.find_by_id(book_id)
        if not book:
            raise ValueError(f"Book {book_id} not found")
        if dto.title is not None:
            book.title = dto.title
        if dto.author is not None:
            book.author = dto.author
        if dto.isbn is not None:
            book.isbn = dto.isbn
        if dto.published_year is not None:
            book.published_year = dto.published_year
        if dto.genre is not None:
            book.genre = dto.genre
        updated = self._repository.update(book)
        return BookResponseDTO.from_entity(updated)


class DeleteBookUseCase:
    """SRP: handles book deletion."""
    
    def __init__(self, repository: BookRepositoryPort):
        self._repository = repository
    
    def execute(self, book_id: int) -> None:
        if not self._repository.delete(book_id):
            raise ValueError(f"Book {book_id} not found")


# ═══════════════════════════════════════════════════════════════
# LAYER 3: INTERFACE ADAPTERS
# ═══════════════════════════════════════════════════════════════

class BookCreateValidator(ValidatorPort):
    """Concrete validator for book creation."""
    
    def validate(self, data: dict) -> List[str]:
        errors = []
        if not data.get("title"):
            errors.append("Title is required")
        if not data.get("author"):
            errors.append("Author is required")
        if not data.get("isbn"):
            errors.append("ISBN is required")
        return errors


class BookController:
    """REST controller - adapts HTTP to use cases."""
    
    def __init__(self, create_uc: CreateBookUseCase,
                 get_uc: GetBookUseCase,
                 list_uc: ListBooksUseCase,
                 update_uc: UpdateBookUseCase,
                 delete_uc: DeleteBookUseCase):
        self._create = create_uc
        self._get = get_uc
        self._list = list_uc
        self._update = update_uc
        self._delete = delete_uc
    
    def handle(self, method: str, path: str,
               data: dict = None) -> dict:
        try:
            if method == "POST" and path == "/books":
                dto = CreateBookDTO(**data)
                result = self._create.execute(dto)
                return {"status": 201, "body": result.to_dict()}
            elif method == "GET" and path == "/books":
                results = self._list.execute()
                return {"status": 200, "body": [r.to_dict() for r in results]}
            elif method == "GET" and path.startswith("/books/"):
                book_id = int(path.split("/")[-1])
                result = self._get.execute(book_id)
                return {"status": 200, "body": result.to_dict()}
            elif method == "PUT" and path.startswith("/books/"):
                book_id = int(path.split("/")[-1])
                dto = UpdateBookDTO(**data)
                result = self._update.execute(book_id, dto)
                return {"status": 200, "body": result.to_dict()}
            elif method == "DELETE" and path.startswith("/books/"):
                book_id = int(path.split("/")[-1])
                self._delete.execute(book_id)
                return {"status": 204, "body": None}
            return {"status": 404, "body": "Not found"}
        except ValueError as e:
            return {"status": 400, "body": str(e)}
        except Exception as e:
            return {"status": 500, "body": str(e)}


# ═══════════════════════════════════════════════════════════════
# LAYER 4: FRAMEWORKS & DRIVERS
# ═══════════════════════════════════════════════════════════════

class InMemoryBookRepository(BookRepositoryPort):
    """Framework-level repository implementation."""
    
    def __init__(self):
        self._store: Dict[int, Book] = {}
        self._next_id = 1
    
    def save(self, book: Book) -> Book:
        book.id = self._next_id
        self._next_id += 1
        self._store[book.id] = book
        return book
    
    def find_by_id(self, book_id: int) -> Optional[Book]:
        return self._store.get(book_id)
    
    def find_all(self) -> List[Book]:
        return list(self._store.values())
    
    def update(self, book: Book) -> Optional[Book]:
        if book.id not in self._store:
            return None
        self._store[book.id] = book
        return book
    
    def delete(self, book_id: int) -> bool:
        if book_id in self._store:
            del self._store[book_id]
            return True
        return False


# ═══════════════════════════════════════════════════════════════
# COMPOSITION ROOT (Dependency Wiring)
# ═══════════════════════════════════════════════════════════════

def create_application() -> BookController:
    """Wire all dependencies following DI principle."""
    repository = InMemoryBookRepository()
    validator = BookCreateValidator()
    create_uc = CreateBookUseCase(repository, validator)
    get_uc = GetBookUseCase(repository)
    list_uc = ListBooksUseCase(repository)
    update_uc = UpdateBookUseCase(repository)
    delete_uc = DeleteBookUseCase(repository)
    return BookController(create_uc, get_uc, list_uc, update_uc, delete_uc)
