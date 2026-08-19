# Generated: rep=5, llm=claude-3.5-sonnet
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
