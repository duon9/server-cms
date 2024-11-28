from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200))
    verified = db.Column(db.Boolean, default=False)   
    role = db.Column(db.String(50), default = 'member')
    create_at = db.Column(db.DateTime, default=datetime.now())

    bookmarks = db.relationship('Bookmark', backref='user', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    borrows = db.relationship('BorrowBook', backref='user', lazy=True)

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now())


class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    rate = db.Column(db.Integer, nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now())


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    cover = db.Column(db.String(200))
    rating = db.Column(db.Float, default=0)
    author = db.Column(db.String(150))
    genre = db.Column(db.String(150))
    year = db.Column(db.String(20))
    publisher = db.Column(db.String(150))
    pdf = db.Column(db.String(150), default = "null")
    video = db.Column(db.String(150), default = "null")
    create_at = db.Column(db.DateTime, default=datetime.now())


    bookmarks = db.relationship('Bookmark', backref='book', lazy=True)
    ratings = db.relationship('Rating', backref='book', lazy=True)
    comments = db.relationship('Comment', backref='book', lazy=True)
    borrows = db.relationship('BorrowBook', backref='book', lazy=True)
    authors = db.relationship('BookAuthor', backref='book', lazy=True)
    genres = db.relationship('BookGenre', backref='book', lazy=True)

class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now())

    books = db.relationship('BookGenre', backref='genre', lazy=True)

class BookAuthor(db.Model):
    __tablename__ = 'book_author'
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), primary_key=True)

class BookGenre(db.Model):
    __tablename__ = 'book_genre'
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), primary_key=True)

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(200)) 
    
    books = db.relationship('BookAuthor', backref='author', lazy=True)

class BorrowBook(db.Model):
    __tablename__ = 'borrow_book'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50))
    start_time = db.Column(db.DateTime, default=datetime.now())
    end_time = db.Column(db.DateTime)
    create_at = db.Column(db.DateTime, default=datetime.now())


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now())

