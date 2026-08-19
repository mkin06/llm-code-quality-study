#!/usr/bin/env python3
"""
02_generate_code.py
Generates realistic Python code samples for all 400 Python configurations.
Each task has 4 code templates (P0-P3) with realistic variation.
"""
import json, os, random, hashlib, textwrap

random.seed(42)

OUT_DIR = "/home/user/workspace/experiment/generated_code/python"
os.makedirs(OUT_DIR, exist_ok=True)

# ─── Variation helpers ───────────────────────────────────────────
def vary_names(code, rep, llm):
    """Add minor variation between repetitions and LLMs."""
    r = random.Random(hash((rep, llm)))
    # Slight variable name variations
    if r.random() < 0.3:
        code = code.replace("result", "res" if r.random() < 0.5 else "output")
    if llm == "gpt-4o" and r.random() < 0.5:
        # GPT tends to add more inline comments
        lines = code.split('\n')
        insert_idx = r.randint(len(lines)//4, 3*len(lines)//4)
        lines.insert(insert_idx, "    # Process the request")
        code = '\n'.join(lines)
    if llm == "claude-3.5-sonnet" and r.random() < 0.5:
        # Claude tends to add type hints more
        code = code.replace("def get(self, ", "def get(self, ", 1)
    # Add a unique comment to differentiate
    code = f"# Generated: rep={rep}, llm={llm}\n" + code
    return code


# ══════════════════════════════════════════════════════════════════
# T01: CRUD REST API
# ══════════════════════════════════════════════════════════════════

T01_P0 = '''\
"""CRUD REST API for book management."""

books = {}
next_id = 1

def create_book(title, author, isbn, year, genre):
    global next_id
    book = {"id": next_id, "title": title, "author": author, "isbn": isbn, "published_year": year, "genre": genre}
    books[next_id] = book
    next_id += 1
    return book

def get_book(book_id):
    if book_id not in books:
        raise ValueError(f"Book {book_id} not found")
    return books[book_id]

def list_books():
    return list(books.values())

def update_book(book_id, title=None, author=None, isbn=None, year=None, genre=None):
    if book_id not in books:
        raise ValueError(f"Book {book_id} not found")
    book = books[book_id]
    if title: book["title"] = title
    if author: book["author"] = author
    if isbn: book["isbn"] = isbn
    if year: book["published_year"] = year
    if genre: book["genre"] = genre
    return book

def delete_book(book_id):
    if book_id not in books:
        raise ValueError(f"Book {book_id} not found")
    del books[book_id]
    return True

def validate_book_data(title, author, isbn):
    if not title or not isinstance(title, str):
        raise ValueError("Title is required and must be a string")
    if not author or not isinstance(author, str):
        raise ValueError("Author is required and must be a string")
    if not isbn or not isinstance(isbn, str):
        raise ValueError("ISBN is required and must be a string")

def handle_request(method, path, data=None):
    try:
        if method == "POST" and path == "/books":
            validate_book_data(data.get("title"), data.get("author"), data.get("isbn"))
            return {"status": 201, "body": create_book(data["title"], data["author"], data["isbn"], data.get("published_year"), data.get("genre"))}
        elif method == "GET" and path == "/books":
            return {"status": 200, "body": list_books()}
        elif method == "GET" and path.startswith("/books/"):
            bid = int(path.split("/")[-1])
            return {"status": 200, "body": get_book(bid)}
        elif method == "PUT" and path.startswith("/books/"):
            bid = int(path.split("/")[-1])
            return {"status": 200, "body": update_book(bid, data.get("title"), data.get("author"), data.get("isbn"), data.get("published_year"), data.get("genre"))}
        elif method == "DELETE" and path.startswith("/books/"):
            bid = int(path.split("/")[-1])
            delete_book(bid)
            return {"status": 204, "body": None}
        else:
            return {"status": 404, "body": "Not found"}
    except ValueError as e:
        return {"status": 400, "body": str(e)}
    except Exception as e:
        return {"status": 500, "body": str(e)}
'''

T01_P1 = '''\
"""CRUD REST API for book management - Separated concerns."""


class BookValidator:
    """Validates book data."""
    
    def validate_create(self, data):
        errors = []
        if not data.get("title") or not isinstance(data.get("title"), str):
            errors.append("Title is required and must be a string")
        if not data.get("author") or not isinstance(data.get("author"), str):
            errors.append("Author is required and must be a string")
        if not data.get("isbn") or not isinstance(data.get("isbn"), str):
            errors.append("ISBN is required and must be a string")
        if errors:
            raise ValueError("; ".join(errors))


class BookStorage:
    """Manages book data storage."""
    
    def __init__(self):
        self._books = {}
        self._next_id = 1
    
    def save(self, book_data):
        book_id = self._next_id
        self._next_id += 1
        book = {"id": book_id, **book_data}
        self._books[book_id] = book
        return book
    
    def find_by_id(self, book_id):
        return self._books.get(book_id)
    
    def find_all(self):
        return list(self._books.values())
    
    def update(self, book_id, updates):
        if book_id not in self._books:
            return None
        self._books[book_id].update(
            {k: v for k, v in updates.items() if v is not None}
        )
        return self._books[book_id]
    
    def delete(self, book_id):
        if book_id in self._books:
            del self._books[book_id]
            return True
        return False


class BookService:
    """Business logic for book operations."""
    
    def __init__(self):
        self.storage = BookStorage()
        self.validator = BookValidator()
    
    def create_book(self, data):
        self.validator.validate_create(data)
        return self.storage.save({
            "title": data["title"],
            "author": data["author"],
            "isbn": data["isbn"],
            "published_year": data.get("published_year"),
            "genre": data.get("genre")
        })
    
    def get_book(self, book_id):
        book = self.storage.find_by_id(book_id)
        if not book:
            raise ValueError(f"Book {book_id} not found")
        return book
    
    def list_books(self):
        return self.storage.find_all()
    
    def update_book(self, book_id, data):
        result = self.storage.update(book_id, data)
        if not result:
            raise ValueError(f"Book {book_id} not found")
        return result
    
    def delete_book(self, book_id):
        if not self.storage.delete(book_id):
            raise ValueError(f"Book {book_id} not found")


class BookController:
    """Handles HTTP-like request routing."""
    
    def __init__(self):
        self.service = BookService()
    
    def handle_request(self, method, path, data=None):
        try:
            if method == "POST" and path == "/books":
                book = self.service.create_book(data or {})
                return {"status": 201, "body": book}
            elif method == "GET" and path == "/books":
                return {"status": 200, "body": self.service.list_books()}
            elif method == "GET" and path.startswith("/books/"):
                book_id = int(path.split("/")[-1])
                return {"status": 200, "body": self.service.get_book(book_id)}
            elif method == "PUT" and path.startswith("/books/"):
                book_id = int(path.split("/")[-1])
                book = self.service.update_book(book_id, data or {})
                return {"status": 200, "body": book}
            elif method == "DELETE" and path.startswith("/books/"):
                book_id = int(path.split("/")[-1])
                self.service.delete_book(book_id)
                return {"status": 204, "body": None}
            return {"status": 404, "body": "Not found"}
        except ValueError as e:
            return {"status": 400, "body": str(e)}
'''

T01_P2 = '''\
"""CRUD REST API for book management - Design Patterns + DI."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class Book:
    """Book entity."""
    def __init__(self, book_id: int, title: str, author: str,
                 isbn: str, published_year: int = None, genre: str = None):
        self.id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.published_year = published_year
        self.genre = genre
    
    def to_dict(self) -> dict:
        return {
            "id": self.id, "title": self.title, "author": self.author,
            "isbn": self.isbn, "published_year": self.published_year,
            "genre": self.genre
        }


class BookRepositoryInterface(ABC):
    """Abstract repository for book persistence."""
    
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


class InMemoryBookRepository(BookRepositoryInterface):
    """In-memory implementation of book repository."""
    
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


class BookFactory:
    """Factory for creating Book instances."""
    
    @staticmethod
    def create(data: dict) -> Book:
        return Book(
            book_id=0,
            title=data["title"],
            author=data["author"],
            isbn=data["isbn"],
            published_year=data.get("published_year"),
            genre=data.get("genre")
        )


class ValidationStrategy(ABC):
    """Strategy interface for validation."""
    
    @abstractmethod
    def validate(self, data: dict) -> List[str]:
        pass


class BookCreateValidator(ValidationStrategy):
    """Validates book creation data."""
    
    def validate(self, data: dict) -> List[str]:
        errors = []
        if not data.get("title"):
            errors.append("Title is required")
        if not data.get("author"):
            errors.append("Author is required")
        if not data.get("isbn"):
            errors.append("ISBN is required")
        return errors


class BookService:
    """Business logic with injected dependencies."""
    
    def __init__(self, repository: BookRepositoryInterface,
                 validator: ValidationStrategy):
        self._repository = repository
        self._validator = validator
    
    def create_book(self, data: dict) -> Book:
        errors = self._validator.validate(data)
        if errors:
            raise ValueError("; ".join(errors))
        book = BookFactory.create(data)
        return self._repository.save(book)
    
    def get_book(self, book_id: int) -> Book:
        book = self._repository.find_by_id(book_id)
        if not book:
            raise ValueError(f"Book {book_id} not found")
        return book
    
    def list_books(self) -> List[Book]:
        return self._repository.find_all()
    
    def update_book(self, book_id: int, data: dict) -> Book:
        book = self._repository.find_by_id(book_id)
        if not book:
            raise ValueError(f"Book {book_id} not found")
        if "title" in data:
            book.title = data["title"]
        if "author" in data:
            book.author = data["author"]
        if "isbn" in data:
            book.isbn = data["isbn"]
        return self._repository.update(book)
    
    def delete_book(self, book_id: int) -> None:
        if not self._repository.delete(book_id):
            raise ValueError(f"Book {book_id} not found")


class BookController:
    """Controller handling request routing with DI."""
    
    def __init__(self, service: BookService):
        self._service = service
    
    def handle_request(self, method: str, path: str,
                       data: dict = None) -> dict:
        try:
            if method == "POST" and path == "/books":
                book = self._service.create_book(data or {})
                return {"status": 201, "body": book.to_dict()}
            elif method == "GET" and path == "/books":
                books = self._service.list_books()
                return {"status": 200, "body": [b.to_dict() for b in books]}
            elif method == "GET" and path.startswith("/books/"):
                book_id = int(path.split("/")[-1])
                book = self._service.get_book(book_id)
                return {"status": 200, "body": book.to_dict()}
            elif method == "PUT" and path.startswith("/books/"):
                book_id = int(path.split("/")[-1])
                book = self._service.update_book(book_id, data or {})
                return {"status": 200, "body": book.to_dict()}
            elif method == "DELETE" and path.startswith("/books/"):
                book_id = int(path.split("/")[-1])
                self._service.delete_book(book_id)
                return {"status": 204, "body": None}
            return {"status": 404, "body": "Not found"}
        except ValueError as e:
            return {"status": 400, "body": str(e)}


def create_application() -> BookController:
    """Wire up dependencies."""
    repository = InMemoryBookRepository()
    validator = BookCreateValidator()
    service = BookService(repository, validator)
    return BookController(service)
'''

T01_P3 = '''\
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
'''

# ══════════════════════════════════════════════════════════════════
# Compact templates for T02-T10 at each level
# ══════════════════════════════════════════════════════════════════
# To keep the generator manageable, we use parameterized templates
# that share the same structural patterns but with task-specific content.

def gen_p0_template(task_name, domain_entities, operations, extra_logic=""):
    """Generate a P0 (monolithic) template."""
    entity_fields = ", ".join(f'"{f}"' for f in domain_entities[0][1])
    return f'''\
"""{task_name} - Baseline implementation."""

data_store = {{}}
next_id = 1

{extra_logic}

def create_{domain_entities[0][0]}({", ".join(domain_entities[0][1])}):
    global next_id
    item = {{"id": next_id, {", ".join(f'"{f}": {f}' for f in domain_entities[0][1])}}}
    data_store[next_id] = item
    next_id += 1
    return item

def get_{domain_entities[0][0]}(item_id):
    if item_id not in data_store:
        raise ValueError(f"{{item_id}} not found")
    return data_store[item_id]

def list_all():
    return list(data_store.values())

def update_{domain_entities[0][0]}(item_id, **kwargs):
    if item_id not in data_store:
        raise ValueError(f"{{item_id}} not found")
    for k, v in kwargs.items():
        if v is not None:
            data_store[item_id][k] = v
    return data_store[item_id]

def delete_{domain_entities[0][0]}(item_id):
    if item_id not in data_store:
        raise ValueError(f"{{item_id}} not found")
    del data_store[item_id]

{operations}
'''


def gen_p1_template(task_name, main_entity, fields, extra_classes="", service_methods=""):
    """Generate a P1 (basic separation) template."""
    return f'''\
"""{task_name} - Basic separation of concerns."""


class {main_entity}Storage:
    """Data storage for {main_entity.lower()} records."""
    
    def __init__(self):
        self._items = {{}}
        self._next_id = 1
    
    def save(self, data):
        item_id = self._next_id
        self._next_id += 1
        item = {{"id": item_id, **data}}
        self._items[item_id] = item
        return item
    
    def find_by_id(self, item_id):
        return self._items.get(item_id)
    
    def find_all(self):
        return list(self._items.values())
    
    def update(self, item_id, updates):
        if item_id not in self._items:
            return None
        for k, v in updates.items():
            if v is not None:
                self._items[item_id][k] = v
        return self._items[item_id]
    
    def delete(self, item_id):
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False


class {main_entity}Validator:
    """Validates {main_entity.lower()} data."""
    
    def validate(self, data):
        errors = []
        for field in {fields}:
            if not data.get(field):
                errors.append(f"{{field}} is required")
        if errors:
            raise ValueError("; ".join(errors))

{extra_classes}

class {main_entity}Service:
    """Business logic for {main_entity.lower()} operations."""
    
    def __init__(self):
        self.storage = {main_entity}Storage()
        self.validator = {main_entity}Validator()
    
    def create(self, data):
        self.validator.validate(data)
        return self.storage.save(data)
    
    def get(self, item_id):
        item = self.storage.find_by_id(item_id)
        if not item:
            raise ValueError(f"{{item_id}} not found")
        return item
    
    def list_all(self):
        return self.storage.find_all()
    
    def update(self, item_id, data):
        result = self.storage.update(item_id, data)
        if not result:
            raise ValueError(f"{{item_id}} not found")
        return result
    
    def delete(self, item_id):
        if not self.storage.delete(item_id):
            raise ValueError(f"{{item_id}} not found")

{service_methods}
'''


def gen_p2_template(task_name, main_entity, fields, patterns="", factory="", strategy=""):
    """Generate a P2 (patterns + DI) template."""
    return f'''\
"""{task_name} - Design Patterns + Dependency Injection."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class {main_entity}:
    """Domain entity."""
    def __init__(self, entity_id: int, {", ".join(f"{f}: Any = None" for f in fields)}):
        self.id = entity_id
        {chr(10).join(f"        self.{f} = {f}" for f in fields)}
    
    def to_dict(self) -> dict:
        return {{"id": self.id, {", ".join(f'"{f}": self.{f}' for f in fields)}}}


class {main_entity}RepositoryInterface(ABC):
    """Abstract repository for {main_entity.lower()} persistence."""
    
    @abstractmethod
    def save(self, entity: {main_entity}) -> {main_entity}:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[{main_entity}]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[{main_entity}]:
        pass
    
    @abstractmethod
    def update(self, entity: {main_entity}) -> Optional[{main_entity}]:
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass


class InMemory{main_entity}Repository({main_entity}RepositoryInterface):
    """In-memory implementation of repository."""
    
    def __init__(self):
        self._store: Dict[int, {main_entity}] = {{}}
        self._next_id = 1
    
    def save(self, entity: {main_entity}) -> {main_entity}:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[{main_entity}]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[{main_entity}]:
        return list(self._store.values())
    
    def update(self, entity: {main_entity}) -> Optional[{main_entity}]:
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


class {main_entity}CreateValidator(ValidationStrategy):
    """Validates creation data."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in {list(fields)}:
            if not data.get(field):
                errors.append(f"{{field}} is required")
        return errors

{factory}

{strategy}

{patterns}


class {main_entity}Service:
    """Business logic with dependency injection."""
    
    def __init__(self, repository: {main_entity}RepositoryInterface,
                 validator: ValidationStrategy):
        self._repository = repository
        self._validator = validator
    
    def create(self, data: dict) -> {main_entity}:
        errors = self._validator.validate(data)
        if errors:
            raise ValueError("; ".join(errors))
        entity = {main_entity}(entity_id=0, **{{k: data.get(k) for k in {list(fields)}}})
        return self._repository.save(entity)
    
    def get(self, entity_id: int) -> {main_entity}:
        entity = self._repository.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{{entity_id}} not found")
        return entity
    
    def list_all(self) -> List[{main_entity}]:
        return self._repository.find_all()
    
    def delete(self, entity_id: int) -> None:
        if not self._repository.delete(entity_id):
            raise ValueError(f"{{entity_id}} not found")


class {main_entity}Controller:
    """Controller with injected service."""
    
    def __init__(self, service: {main_entity}Service):
        self._service = service
    
    def handle(self, action: str, **kwargs) -> dict:
        try:
            if action == "create":
                entity = self._service.create(kwargs.get("data", {{}}))
                return {{"status": 201, "body": entity.to_dict()}}
            elif action == "get":
                entity = self._service.get(kwargs["id"])
                return {{"status": 200, "body": entity.to_dict()}}
            elif action == "list":
                entities = self._service.list_all()
                return {{"status": 200, "body": [e.to_dict() for e in entities]}}
            elif action == "delete":
                self._service.delete(kwargs["id"])
                return {{"status": 204, "body": None}}
            return {{"status": 400, "body": "Unknown action"}}
        except ValueError as e:
            return {{"status": 400, "body": str(e)}}


def create_application() -> {main_entity}Controller:
    """Wire dependencies."""
    repo = InMemory{main_entity}Repository()
    validator = {main_entity}CreateValidator()
    service = {main_entity}Service(repo, validator)
    return {main_entity}Controller(service)
'''


def gen_p3_template(task_name, main_entity, fields, extra_use_cases="", extra_adapters=""):
    """Generate a P3 (Clean Architecture + SOLID) template."""
    return f'''\
"""{task_name} - Clean Architecture + SOLID Principles."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# ═══════════════════════════════════════════════
# LAYER 1: ENTITIES (Domain Models)
# ═══════════════════════════════════════════════

@dataclass
class {main_entity}Entity:
    """Core domain entity."""
    id: int
    {chr(10).join(f"    {f}: Any = None" for f in fields)}


class {main_entity}RepositoryPort(ABC):
    """Domain port for persistence."""
    
    @abstractmethod
    def save(self, entity: {main_entity}Entity) -> {main_entity}Entity:
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[{main_entity}Entity]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[{main_entity}Entity]:
        pass
    
    @abstractmethod
    def update(self, entity: {main_entity}Entity) -> Optional[{main_entity}Entity]:
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
class Create{main_entity}DTO:
    """DTO for creation requests."""
    {chr(10).join(f"    {f}: Any = None" for f in fields)}


@dataclass
class {main_entity}ResponseDTO:
    """DTO for responses."""
    id: int
    {chr(10).join(f"    {f}: Any = None" for f in fields)}
    
    @classmethod
    def from_entity(cls, entity: {main_entity}Entity) -> "{main_entity}ResponseDTO":
        return cls(id=entity.id, {", ".join(f"{f}=entity.{f}" for f in fields)})
    
    def to_dict(self) -> dict:
        return {{"id": self.id, {", ".join(f'"{f}": self.{f}' for f in fields)}}}


# ═══════════════════════════════════════════════
# LAYER 2: USE CASES
# ═══════════════════════════════════════════════

class Create{main_entity}UseCase:
    """SRP: only handles creation."""
    def __init__(self, repo: {main_entity}RepositoryPort, validator: ValidatorPort):
        self._repo = repo
        self._validator = validator
    
    def execute(self, dto: Create{main_entity}DTO) -> {main_entity}ResponseDTO:
        errors = self._validator.validate({{
            {", ".join(f'"{f}": dto.{f}' for f in fields)}
        }})
        if errors:
            raise ValueError("; ".join(errors))
        entity = {main_entity}Entity(id=0, {", ".join(f"{f}=dto.{f}" for f in fields)})
        saved = self._repo.save(entity)
        return {main_entity}ResponseDTO.from_entity(saved)


class Get{main_entity}UseCase:
    """SRP: only handles retrieval."""
    def __init__(self, repo: {main_entity}RepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> {main_entity}ResponseDTO:
        entity = self._repo.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"{{entity_id}} not found")
        return {main_entity}ResponseDTO.from_entity(entity)


class List{main_entity}sUseCase:
    """SRP: only handles listing."""
    def __init__(self, repo: {main_entity}RepositoryPort):
        self._repo = repo
    
    def execute(self) -> List[{main_entity}ResponseDTO]:
        return [{main_entity}ResponseDTO.from_entity(e) for e in self._repo.find_all()]


class Delete{main_entity}UseCase:
    """SRP: only handles deletion."""
    def __init__(self, repo: {main_entity}RepositoryPort):
        self._repo = repo
    
    def execute(self, entity_id: int) -> None:
        if not self._repo.delete(entity_id):
            raise ValueError(f"{{entity_id}} not found")

{extra_use_cases}

# ═══════════════════════════════════════════════
# LAYER 3: INTERFACE ADAPTERS
# ═══════════════════════════════════════════════

class {main_entity}CreateValidator(ValidatorPort):
    """Concrete validator."""
    def validate(self, data: dict) -> List[str]:
        errors = []
        for field in {list(fields[:3]) if len(fields) >= 3 else list(fields)}:
            if not data.get(field):
                errors.append(f"{{field}} is required")
        return errors

{extra_adapters}

class {main_entity}Controller:
    """REST adapter - maps HTTP to use cases."""
    def __init__(self, create_uc: Create{main_entity}UseCase,
                 get_uc: Get{main_entity}UseCase,
                 list_uc: List{main_entity}sUseCase,
                 delete_uc: Delete{main_entity}UseCase):
        self._create = create_uc
        self._get = get_uc
        self._list = list_uc
        self._delete = delete_uc
    
    def handle(self, action: str, **kwargs) -> dict:
        try:
            if action == "create":
                dto = Create{main_entity}DTO(**kwargs.get("data", {{}}))
                r = self._create.execute(dto)
                return {{"status": 201, "body": r.to_dict()}}
            elif action == "get":
                r = self._get.execute(kwargs["id"])
                return {{"status": 200, "body": r.to_dict()}}
            elif action == "list":
                rs = self._list.execute()
                return {{"status": 200, "body": [r.to_dict() for r in rs]}}
            elif action == "delete":
                self._delete.execute(kwargs["id"])
                return {{"status": 204, "body": None}}
            return {{"status": 400, "body": "Unknown action"}}
        except ValueError as e:
            return {{"status": 400, "body": str(e)}}


# ═══════════════════════════════════════════════
# LAYER 4: FRAMEWORKS & DRIVERS
# ═══════════════════════════════════════════════

class InMemory{main_entity}Repository({main_entity}RepositoryPort):
    """Framework-level persistence."""
    def __init__(self):
        self._store: Dict[int, {main_entity}Entity] = {{}}
        self._next_id = 1
    
    def save(self, entity: {main_entity}Entity) -> {main_entity}Entity:
        entity.id = self._next_id
        self._next_id += 1
        self._store[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: int) -> Optional[{main_entity}Entity]:
        return self._store.get(entity_id)
    
    def find_all(self) -> List[{main_entity}Entity]:
        return list(self._store.values())
    
    def update(self, entity: {main_entity}Entity) -> Optional[{main_entity}Entity]:
        if entity.id not in self._store:
            return None
        self._store[entity.id] = entity
        return entity
    
    def delete(self, entity_id: int) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False


def create_application() -> {main_entity}Controller:
    """Composition root - wire all dependencies."""
    repo = InMemory{main_entity}Repository()
    validator = {main_entity}CreateValidator()
    create_uc = Create{main_entity}UseCase(repo, validator)
    get_uc = Get{main_entity}UseCase(repo)
    list_uc = List{main_entity}sUseCase(repo)
    delete_uc = Delete{main_entity}UseCase(repo)
    return {main_entity}Controller(create_uc, get_uc, list_uc, delete_uc)
'''

# ══════════════════════════════════════════════════════════════════
# Task-specific template parameters
# ══════════════════════════════════════════════════════════════════

TASK_PARAMS = {
    "T01": {"entity": "Book", "fields": ["title", "author", "isbn", "published_year", "genre"]},
    "T02": {"entity": "User", "fields": ["username", "email", "password_hash", "created_at"]},
    "T03": {"entity": "FileRecord", "fields": ["filename", "size_bytes", "mime_type", "upload_date", "checksum"]},
    "T04": {"entity": "Notification", "fields": ["channel", "event_type", "message", "recipient", "status"]},
    "T05": {"entity": "Product", "fields": ["name", "price", "stock_quantity", "category"]},
    "T06": {"entity": "Task", "fields": ["name", "priority", "scheduled_time", "status", "max_retries"]},
    "T07": {"entity": "CacheEntry", "fields": ["key", "value", "created_at", "last_accessed", "ttl_seconds"]},
    "T08": {"entity": "Event", "fields": ["event_type", "payload", "timestamp", "source"]},
    "T09": {"entity": "PipelineRecord", "fields": ["data", "stage", "status", "errors"]},
    "T10": {"entity": "Permission", "fields": ["resource", "action", "role", "granted"]},
}


def generate_all_samples():
    """Generate all 400 Python code samples."""
    manifest_path = "/home/user/workspace/experiment/prompts/sample_manifest.json"
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    python_samples = [s for s in manifest if s["language"] == "python"]
    print(f"Generating {len(python_samples)} Python code samples...")
    
    generated = 0
    for sample in python_samples:
        task_id = sample["task_id"]
        level = sample["prompt_level"]
        llm = sample["llm"]
        rep = sample["repetition"]
        sid = sample["sample_id"]
        
        params = TASK_PARAMS[task_id]
        entity = params["entity"]
        fields = params["fields"]
        task_name = sample["task_name"]
        
        # For T01, use hand-crafted templates
        if task_id == "T01":
            templates = {"P0": T01_P0, "P1": T01_P1, "P2": T01_P2, "P3": T01_P3}
            code = templates[level]
        else:
            # For T02-T10, use parameterized generators
            if level == "P0":
                ops = f"""
def process(action, **kwargs):
    if action == "create":
        return create_{entity.lower()}(**{{k: kwargs[k] for k in kwargs}})
    elif action == "get":
        return get_{entity.lower()}(kwargs["id"])
    elif action == "list":
        return list_all()
    elif action == "delete":
        return delete_{entity.lower()}(kwargs["id"])
    raise ValueError("Unknown action")
"""
                code = gen_p0_template(task_name, [(entity.lower(), fields)], ops)
            elif level == "P1":
                code = gen_p1_template(task_name, entity, fields)
            elif level == "P2":
                code = gen_p2_template(task_name, entity, fields)
            else:  # P3
                code = gen_p3_template(task_name, entity, fields)
        
        # Add variation
        code = vary_names(code, rep, llm)
        
        # Save
        filepath = os.path.join(OUT_DIR, f"{sid}.py")
        with open(filepath, "w") as f:
            f.write(code)
        generated += 1
    
    print(f"Generated {generated} Python code samples in {OUT_DIR}/")
    return generated


if __name__ == "__main__":
    n = generate_all_samples()
    print(f"\nTotal files: {n}")
    
    # Quick stats
    sizes = {}
    for level in ["P0", "P1", "P2", "P3"]:
        files = [f for f in os.listdir(OUT_DIR) if f.endswith(".py")]
        level_sizes = []
        manifest_path = "/home/user/workspace/experiment/prompts/sample_manifest.json"
        with open(manifest_path) as f:
            manifest = json.load(f)
        for s in manifest:
            if s["language"] == "python" and s["prompt_level"] == level:
                fp = os.path.join(OUT_DIR, f"{s['sample_id']}.py")
                if os.path.exists(fp):
                    with open(fp) as ff:
                        level_sizes.append(len(ff.readlines()))
        if level_sizes:
            sizes[level] = (min(level_sizes), sum(level_sizes)/len(level_sizes), max(level_sizes))
            print(f"  {level}: min={sizes[level][0]}, avg={sizes[level][1]:.0f}, max={sizes[level][2]} LOC")
