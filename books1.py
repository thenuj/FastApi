from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel,Field


class Book:
    id: int
    title: str
    author : str
    desc: str
    rating: str

    def __init__(self, id, title, author, desc, rating):
        self.id = id
        self.title = title
        self.author = author
        self.desc = desc
        self.rating = rating


class BookRequest(BaseModel):
    id: Optional[int] = None # This can be an integer or it may be nothing
    title: str = Field(min_length=3)
    author: str = Field(min_length=4)
    desc: str = Field(max_length=20)
    rating: int = Field(gt=0,lt=6) # 1-5 range

    model_config = {
        "json_schema_extra":{
            "example":{
                "title": "A new Book",
                "author": "Coder",
                "desc": "Describing the book",
                "rating" : 5
            }
        }
    }
BOOKS=[
    Book(1, "ABC", "Anuj", "adsglasdgasdb", 10),
    Book(2, "def", "Abhi", "adsglasdgasdb", 5),
    Book(3, "hij", "Tikhe", "adsglasdgasdb", 6),
    Book(4, "jkl", "Harshu", "adsglasdgasdb", 16),
    Book(5, "mno", "Babu", "adsglasdgasdb", 18),
    Book(6, "pqr", "Guddu", "adsglasdgasdb", 11),
]

app = FastAPI()

@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/books/{book_id}")
async def read_book_by_id(book_id:int):
    for book in BOOKS:
        if book.id == book_id:
            return book
    return {"Error": "Book not found"}


@app.get("/books/")
async def read_books_by_rating(book_rating:int):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
            return books_to_return
    return {"Error": "Book not found"}

@app.post("/books/create_book")
async def create_book(book_request:BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))

@app.put("/books/update_book")
async def update_book_by_id(book:BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i]=Book(**book.model_dump())
            return {"message": "Book Updated"}


def find_book_id(book: Book):
    if(len(BOOKS))>0:
        book.id = BOOKS[-1].id + 1
    else:
        book.id = 1
    return book