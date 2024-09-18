from fastapi import Body,FastAPI

app = FastAPI()

BOOKS = [
    {'title':'Title One', 'author':'Author One', 'category':'science'},
    {'title':'Title Two', 'author':'Author Two', 'category':'History'},
    {'title':'Title Three', 'author':'Author Three', 'category':'Maths'},
    {'title':'Title Four', 'author':'Author Two', 'category':'History'},
    {'title':'Title Five', 'author':'Author One', 'category':'English'}
]

@app.get("/books")
def read_all_books():
    return BOOKS

# example for path parameter
@app.get("/books/{book_title}")
async def read_book(book_title:str):
    for x in BOOKS:
        if x.get('title').casefold() == book_title.casefold():
            return x
        else:
            return {'message': 'Book not '}

# example for query parameter
@app.get("/books/")
async def read_category_by_query(category:str):
    books = []
    for x in BOOKS:
        if x.get('category').casefold() == category.casefold():
            books.append(x)
    return books

# We can also combine both path and query param eg of URL is given below
# http://127.0.0.1:49881/books/title%20two/?category=history
@app.get("/books/{book_title}/")
async def read_category_by_path_and_query(book_title:str,category:str):
    books = []
    for x in BOOKS:
        if (x.get('category').casefold() == category.casefold() and
                x.get('title').casefold()==book_title.casefold()):
            books.append(x)
    return books

@app.post("/books/create_book")
async def create_book(new_book = Body()):
    BOOKS.append(new_book)

@app.put("/books/update_book")
async def update_book(update_book = Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold()==update_book.get('title').casefold():
            BOOKS[i] = update_book

@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title:str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold()==book_title.casefold():
            BOOKS.pop(i)
            break