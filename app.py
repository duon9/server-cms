from flask import Flask, render_template, request, redirect, url_for, flash, abort
from models import db, User, Book, Comment, BorrowBook, Bookmark, Rating, Genre, BookAuthor, BookGenre, Author
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from flask_socketio import SocketIO, emit
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS
from flask import jsonify
import utils
from sqlalchemy import func
import time
import datetime
import random
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.query import Prefix



app = Flask(__name__)
app.config.from_object('config.Config')

# CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25, transports=["websocket"])
# Khởi tạo SQLAlchemy
db.init_app(app)

migrate = Migrate(app, db)
admin = Admin(app, name='My Admin', template_mode='bootstrap3')

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Bookmark, db.session))
admin.add_view(ModelView(Rating, db.session))
admin.add_view(ModelView(Book, db.session))
admin.add_view(ModelView(Genre, db.session))
admin.add_view(ModelView(BookAuthor, db.session))
admin.add_view(ModelView(BookGenre, db.session))
admin.add_view(ModelView(Author, db.session))
admin.add_view(ModelView(BorrowBook, db.session))
admin.add_view(ModelView(Comment, db.session))


with app.app_context():
    db.create_all()

@app.route('/')
async def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

@app.route('/<int:id>')
async def borrow_book_detail(id):
    borrow = BorrowBook.query.filter_by(id=id).first()
    if not borrow:
        abort(404)  

    book = Book.query.filter_by(id=borrow.book_id).first()
    if not book:
        abort(404)  

    data = {
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "cover": book.cover,
        "year": book.year,
        "start_time": borrow.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": borrow.end_time.strftime("%Y-%m-%d %H:%M:%S") if borrow.end_time else "Chưa trả",
        "status": borrow.status,
    }

    return render_template('borrow_detail.html', data=data)



@app.route('/book/<int:book_id>')
async def book_detail(book_id):
    book = utils.get_book(book_id = book_id)
    comments = Comment.query.filter_by(book_id=book_id).all()
    return render_template('book_detail.html', book=book, comments=comments)

@app.route('/add_book', methods=['GET', 'POST'])
async def add_book():
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        description = request.form['description']
        stock = 100
        cover = request.form['cover']
        author = request.form['author']
        genre = request.form['genre']
        publisher = request.form["publisher"]
        year = request.form["year"]
        pdf = request.form["pdf"]        
        
        # Tạo một đối tượng sách mới
        new_book = Book(isbn=isbn, title=title, description=description, stock=stock, cover=cover, rating = 1.0, author = author, genre = genre, publisher = publisher, year = year, pdf = pdf)

        try:
            # Thêm vào cơ sở dữ liệu
            db.session.add(new_book)
            db.session.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('add_book'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: Book already exists or invalid data!', 'danger')

    return render_template('add_book.html')

@app.route('/test_socket')
def test_socket():
    return render_template('test_socket.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message', {'msg': 'Welcome to the server!'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    
@socketio.on('login')
def handle_login(data):
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username = username).first()
    
    if user and user.password == password:
        response = {
            'status': 'success',
            'id': user.id,
            'username': user.username,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'role' : user.role
        }
    else:
        response = {
            'status': 'failure',
            'message': 'Invalid username or password'
        }

    emit('login_response', response)
    
@socketio.on('register')
def handle_register(data):
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user:
        response = {
           'status': 'failure',
           'message': 'Username already exist'
        }
        emit('register_response', response)
        return
        
    new_user = User(
                username = username,
                password = password,
                firstname = firstname,
                lastname = lastname,
                role = "member"
                )
    
    db.session.add(new_user)
    db.session.commit()
    
    response = {
        'status': 'success',
        'message': 'User registered successfully'
    }
    emit('register_response', response)
    
@socketio.on('get_feature_book')
def get_feature_book(data):
    book_count = Book.query.count()
    
    if (book_count > 0):
        random_idx = random.randint(0, book_count - 1)
        
        book = Book.query.offset(random_idx).first()
        
        feature_book = {
            "status": "success",
            "id": book.id,
            "cover": book.cover,
            "title": book.title,
            "description": book.description,
            "isbn": book.isbn,
            "author": book.author
        }
        
        emit("feature_book_response", feature_book)
        
@socketio.on('get_new_arrival_book')
def get_new_arrival_book(data):
    new_arrivals = Book.query.order_by(Book.id.desc()).limit(4).all()
    
    if new_arrivals:
        response = {
            "status": "success",
            "books": [
                {
                    "id": book.id,
                    "cover": book.cover,
                    "title": book.title
                } for book in new_arrivals
            ]
        }
        emit("new_arrival_book_response", response)
    else:
        emit("new_arrival_book_response", {
            "status": "failure",
            "message": "No new arrivals available."
        })

@socketio.on('get_popular_book')
def get_popular_book(data):
    populars = Book.query.order_by(Book.id.desc()).limit(4).all()
    
    if populars:
        response = {
            "status": "success",
            "books": [
                {
                    "id": book.id,
                    "cover": book.cover,
                    "title": book.title
                } for book in populars
            ]
        }
        emit("popular_book_response", response)
    else:
        emit("popular_book_response", {
            "status": "failure",
            "message": "No popular book available."
        })
        
@socketio.on("get_book_detail")
def get_book_detail(data):
    book_id = data.get("book_id")
    user_id = data.get("user_id")
    print(book_id)
    if not book_id:
        emit("book_detail_response", {
            "status": "failure",
            "message": "No book ID provided."
        })
        return

    book = Book.query.filter_by(id=book_id).first()
    
    if book:
        available = book.stock - utils.get_unavailable_book(book_id=book_id)
        borrow_state = utils.get_book_borrow_state(user_id=user_id, book_id=book_id)
        state = utils.get_bookmark_state(user_id=user_id, book_id = book_id)
        
        if (state is not None):
            bookmark = True
        else:
            bookmark = False
        
        if borrow_state:
            borrow = True
            borrow_id = borrow_state.id
        else:
            borrow = False
            borrow_id = -1
        response = {
            "status": "success",
            "id": book.id,
            "cover": book.cover,
            "isbn" : book.isbn,
            "title": book.title,
            "author": book.author,  
            "genre" : book.genre,
            "publisher": book.publisher,  
            "year": book.year,
            "available": available,
            "rating" : utils.get_book_avg_rating(book_id=book_id),
            "description": book.description, 
            "borrow": borrow,
            "pdf": book.pdf,
            "borrow_id": borrow_id,
            "bookmark": bookmark
        }
        emit("book_detail_response", response)
    else:
        emit("book_detail_response", {
            "status": "failure",
            "message": "Book not found."
        })
        
@socketio.on("post_comment")
def post_comment(data):
    book_id = data.get("book_id")
    user_id = data.get("user_id")
    content = data.get("content")
    print(content)

    comment = Comment(book_id=book_id, user_id=user_id, content=content)

    try:
        db.session.add(comment)
        db.session.commit()

        user = User.query.filter_by(id = user_id).first()
        if user.avatar is None:
            avatar = "https://semihanoi.vinasa.org.vn/wp-content/uploads/2024/07/chuductrinh1.jpg"
            print(avatar)
        else:
            avatar = user.avatar
            
        print("send reply")
        emit("get_comment_response", {
            "message": "comment",
            "username": user.username,
            "avatar": avatar,
            "book_id": book_id,
            "user_id": user_id,
            "content": content,
            "datetime": "today"
        })
    except Exception as e:
        db.session.rollback()
        emit("get_comment_response", {
            "status": "failure",
            "message": "An error occurred while posting the comment.",
            "error": str(e)
        })
        
@socketio.on("get_all_comment")
def get_all_comment(data):
    book_id = data.get("book_id")

    comments = Comment.query.filter_by(book_id = book_id)
    
    
    for comment in comments:
        
        user = User.query.filter_by(id = comment.user_id).first()
        if user.avatar is None:
            avatar = "https://i1-vnexpress.vnecdn.net/2022/08/14/ts-chu-duc-trinh-1660296689-39-9247-7011-1660474493.jpg?w=1020&h=0&q=100&dpr=1&fit=crop&s=pMxvcDPtgfUdk3slWcLfKg"
            print(avatar)
        else:
            avatar = user.avatar
        
        emit("get_comment_response", {
            "message": "comment",
            "username": user.username,
            "avatar": avatar,
            "book_id": book_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "datetime": "today"
        })
        
@socketio.on("borrow_book")
def borrow_book(data):
    user_id = data.get("user_id")
    book_id = data.get("book_id")
    status = data.get("status")
    
    if (status == "borrow"):
        print("a")
        borrow_book_state = utils.get_book_borrow_state(user_id=user_id, book_id= book_id)
        if (borrow_book_state):
            return
        borrow_book = BorrowBook(user_id = user_id, book_id = book_id, status = "WAITING", end_time = datetime.datetime.now() + datetime.timedelta(days=30))
        
        try:
            db.session.add(borrow_book)
            db.session.commit()
            
            emit("borrow_book_response", {
                "status": "borrow_success"
            })
        except Exception as e:
            print(e)
    else:
        print("b")
        borrow_book = utils.get_book_borrow_state(user_id=user_id, book_id=book_id)
        borrow_book.end_time = datetime.datetime.now() - datetime.timedelta(seconds=10)
        borrow_book.status = "RETURN"
        db.session.commit()
        
        emit("borrow_book_response", {
                "status": "return_success"
        })
        
@socketio.on("search")
def search(data):
    print("receive")
    query = data["query"]
    
    ix = open_dir("indexdir")
    searcher = ix.searcher()
    fields = ["title", "genre", "author", "publisher"]
    query_parser = QueryParser("title", schema=ix.schema)
    
    prefix_query = Prefix("title", query) 

    results = searcher.search(prefix_query, limit=5)
    
    search_results = []
    
    for result in results:
        book = utils.get_book(result["id"])
        search_results.append({
            "id": result["id"],
            "title": result["title"],
            "cover": book.cover,
            "author": result.get("author", "Unknown"),
            "genre": result.get("genre", "Unknown"),
            "publisher": result.get("publisher", "Unknown"),
        })
        
    if (len(search_results) != 0):
        emit("search_results", {
            "status": "success",
            "results": search_results
        })
    else:
        emit("search_results", {
            "status": "failure",
        })
    
    searcher.close()
        
    
@socketio.on("get_borrow_book_list")
def get_borrow_book_list(data):
    user_id = data.get("user_id")
    print(user_id)
    book_borrows = utils.get_borrow_book(user_id=user_id)
    
    books = []
    if book_borrows is not None:
        for book_borrow in book_borrows:
            book = Book.query.filter_by(id = book_borrow.book_id).first()
            books.append({
                "id": book.id,
                "cover": book.cover,
                "title": book.title
            })
            
        emit("borrow_book_list_response", {
            "status" : "success",
            "books" : books
        })
    else:
        emit("borrow_book_list_response", {
            "status" : "failure",
        })
        
@socketio.on("set_bookmark")
def set_bookmark(data):
    user_id = data.get("user_id")
    book_id = data.get("book_id")
    
    state = utils.get_bookmark_state(user_id= user_id, book_id= book_id)
    
    if (state is None):
        bookmark = Bookmark(user_id = user_id, book_id = book_id)
        
        try:
            db.session.add(bookmark)
            db.session.commit()
            
            emit("bookmark_response", {
                "status": "bookmark_success"
            })
        except Exception as e:
            print(e)
    else:
        try:
            db.session.delete(state)
            db.session.commit()
            
            emit("bookmark_response", {
                "status": "unbookmark_success"
            })
        except Exception as e:
            print(e)

@socketio.on("get_bookmark_list")
def get_bookmark_list(data):
    user_id = data.get("user_id")
    
    bookmarks = utils.get_all_bookmark(user_id)
    
    books = []
    if bookmarks is not None:
        for bookmark in bookmarks:
            book = Book.query.filter_by(id = bookmark.book_id).first()
            books.append({
                "id": book.id,
                "cover": book.cover,
                "title": book.title
            })
            
        emit("bookmark_list_response", {
            "status" : "success",
            "books" : books
        })
    else:
        emit("bookmark_list_response", {
            "status" : "failure",
        })
        
@socketio.on("set_rating")
def rating_response(data):
    
    user_id = data.get("user_id")
    book_id = data.get("book_id")
    rating_value = data.get("rating")
    
    print(rating_value)
    rate = utils.get_rating(user_id=user_id, book_id= book_id)
    
    if (rate is not None):
        rate.rate = rating_value
        db.session.commit()
    else:
        rate = Rating(user_id = user_id, book_id = book_id, rate = rating_value)
        try:
            db.session.add(rate)
            db.session.commit()
        except Exception as e:
            print(e)
    
    emit("rating_response", {
        "status" : "rating_success",
        "rating" : rating_value
    })
    
@socketio.on("get_user_rating")
def get_user_rating(data):
    user_id = data.get("user_id")
    book_id = data.get("book_id")
    
    rating = utils.get_rating(user_id= user_id, book_id= book_id)
    
    if (rating):
        emit("user_rating_response", {
            "status" : "success",
            "rating" : rating.rate
        })
    else:
        emit("user_rating_response", {
            "status" : "success",
            "rating" : 0
        })
        
@socketio.on("get_borrow_state")
def get_borrow_state(data):
    user_id = data.get("user_id")
    book_id = data.get("book_id")
    
    state = utils.get_book_borrow_state(user_id= user_id , book_id= book_id)
    
    if (state):
        emit("borrow_state_response", {
            "status": "success",
            "code" : state.id
        })
    else:
        emit("borrow_state_response", {
            "status" : "failure",
        })

@socketio.on("get_user")
def get_user(data):
    user_id = data.get("user_id")
    
    user = User.query.filter_by(id = user_id).first()
    
    if (user):
        
        if (user.avatar):
            avatar = user.avatar
        else:
            avatar = "https://fastly.picsum.photos/id/454/200/200.jpg?hmac=N13wDge6Ku6Eg_LxRRsrfzC1A4ZkpCScOEp-hH-PwHg"
        
        # print(type(utils.get_total_book_count))
        # print(type(utils.get_read_book_count(user_id = user_id)))
        result = utils.get_recent_book_finishes(user_id = user_id)
        
        data = [
            {
                "day": finish_day.strftime("%Y-%m-%d"),  
                "bookfinish": bookfinish
            }
            for finish_day, bookfinish in result
        ]
        
        emit("user_response", {
            "status" : "success",
            "username" : user.username,
            "firstname" : user.firstname,
            "lastname" : user.lastname,
            "avatar" : avatar,
            "totalbook" : utils.get_total_book_count(),
            "readbook" : utils.get_read_book_count(user_id = user_id),
            "recent" : data,
            "last" : utils.get_user_last(user_id= user_id)
        })
if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000, debug=True) 

