# Generated: rep=2, llm=gpt-4o
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
