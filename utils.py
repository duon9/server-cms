from models import db, User, Book, Comment, BorrowBook, Bookmark, Rating, Genre, BookAuthor, BookGenre, Author
import datetime
from sqlalchemy import func

def add_book(isbn, title, description, stock, cover, author, genre):
    pass

def get_unavailable_book(book_id):
    count = BorrowBook.query.filter(
        BorrowBook.book_id == book_id,
        BorrowBook.end_time > datetime.datetime.now()
    ).count()
    
    return count

def get_borrow_book(user_id):
    books = BorrowBook.query.filter(
        BorrowBook.user_id == user_id,
        BorrowBook.end_time > datetime.datetime.now()
    ).all()
    
    return books

def get_book_avg_rating(book_id):
    avg_rating = db.session.query(func.avg(Rating.rate)) \
        .filter(Rating.book_id == book_id) \
        .scalar()
    
    if avg_rating == None:
        avg_rating = 0
    return avg_rating

def get_book_borrow_state(user_id, book_id):
    borrow_state = BorrowBook.query.filter(
        BorrowBook.book_id == book_id,
        BorrowBook.user_id == user_id,
        BorrowBook.end_time > datetime.datetime.now()
    ).first()
    
    return borrow_state

def get_rating(user_id, book_id):
    rate = Rating.query.filter_by(user_id= user_id, book_id = book_id).first()  
    return rate  

def get_book(id):
    book = Book.query.filter_by(id = id).first()
    return book

def get_bookmark_state(user_id, book_id):
    state = Bookmark.query.filter_by(user_id = user_id, book_id = book_id).first()
    
    return state

def get_all_bookmark(user_id):
    bookmarks = Bookmark.query.filter_by(user_id = user_id).all()
    return bookmarks

def get_total_book_count():
    count = db.session.query(func.count(Book.id)).scalar()
    return count

def get_read_book_count(user_id):
    count = db.session.query(func.count(func.distinct(BorrowBook.book_id))) \
        .filter(BorrowBook.user_id == user_id, BorrowBook.status == "RETURN") \
        .scalar() or 0
    return count

def get_recent_book_finishes(user_id):
    try:
        result = (
            db.session.query(
                BorrowBook.end_time.label("day"),  
                func.count(func.distinct(BorrowBook.book_id)).label("bookfinish")
            )
            .filter(BorrowBook.status == "RETURN", BorrowBook.user_id == user_id) 
            .group_by(BorrowBook.end_time)
            .order_by(BorrowBook.end_time.desc())
            # .limit(3)
            .all()
        )
        
        return result
    except Exception as e:
        print(f"Error in get_recent_book_finishes: {e}")
        return []
    
def get_user_last(user_id):
    user = User.query.filter_by(id = user_id).first()
    
    current_day = datetime.datetime.now()
    
    create_day = user.create_at
    
    return (current_day - create_day).days
    
    