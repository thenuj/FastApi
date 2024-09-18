from typing import Optional
from fastapi import FastAPI,HTTPException,Path,Query
from pydantic import BaseModel,Field

# with the help of Path and query we can add data validation to path and query parameters.

class Book:
    id: int
    title: str
    author : str
    desc: str
    rating: str
    pub_date:int

    def __init__(self, id, title, author, desc, rating, pub_date):
        self.id = id
        self.title = title
        self.author = author
        self.desc = desc
        self.rating = rating
        self.pub_date = pub_date


class BookRequest(BaseModel):
    id: Optional[int] = None # This can be an integer or it may be nothing
    title: str = Field(min_length=3)
    author: str = Field(min_length=4)
    desc: str = Field(max_length=20)
    rating: int = Field(gt=0,lt=6) # 1-5 range
    pub_date : int = Field(gt=1999,lt=2024)

    model_config = {
        "json_schema_extra":{
            "example":{
                "title": "A new Book",
                "author": "Coder",
                "desc": "Describing the book",
                "rating" : 5,
                "pub_date":2000
            }
        }
    }
BOOKS=[
    Book(1, "ABC", "Anuj", "adsglasdgasdb", 10,2012),
    Book(2, "def", "Abhi", "adsglasdgasdb", 5,2016),
    Book(3, "hij", "Tikhe", "adsglasdgasdb", 6,2018),
    Book(4, "jkl", "Harshu", "adsglasdgasdb", 16,2020),
    Book(5, "mno", "Babu", "adsglasdgasdb", 18,2022),
    Book(6, "pqr", "Guddu", "adsglasdgasdb", 11,1996),
]

app = FastAPI()

@app.get("/books")
async def read_all_books():
    return BOOKS,HTTPException(200,detail="Request Successful")

@app.get("/books/{book_id}")
async def read_book_by_id(book_id:int):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(404,detail='Item Not Found')

@app.get("/books/")
async def read_books_by_rating(book_rating:int):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
            return books_to_return
    raise HTTPException(404,detail='Item Not Found')

@app.post("/books/create_book")
async def create_book(book_request:BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))

@app.put("/books/update_book")
async def update_book_by_id(book:BookRequest):
    book_updated = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i]=Book(**book.model_dump())
            book_updated = True
            return HTTPException(200,detail='Book updated successfully')
    if not book_updated:
        raise HTTPException(404, detail='Item Not Found')

@app.delete("/books/{book_id}")
async def delete_book_by_id(book_id:int):
    book_deleted = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_deleted = True
            break
    if not book_deleted:
        raise HTTPException(404, detail='Item Not Found')

@app.get("/books/publish/{date}")
async def read_book_by_pub_date(date:int):
    books_to_return = []
    for book in BOOKS:
        if book.pub_date == date:
            books_to_return.append(book)
    if len(books_to_return)>0:
        return books_to_return
    else:
        raise HTTPException(404, detail='Item Not Found')



def find_book_id(book: Book):
    if(len(BOOKS))>0:
        book.id = BOOKS[-1].id + 1
    else:
        book.id = 1
    return book