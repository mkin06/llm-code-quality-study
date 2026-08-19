# Generated: rep=4, llm=claude-3.5-sonnet
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
