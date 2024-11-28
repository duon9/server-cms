import sqlite3
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
import os

# Kết nối tới CSDL
conn = sqlite3.connect('db.sqlite3')  # Thay 'database.db' bằng đường dẫn đến CSDL của bạn
cursor = conn.cursor()

# Định nghĩa schema cho Whoosh với các trường cần lập chỉ mục
schema = Schema(
    id=ID(stored=True),                   # Lưu id để truy xuất
    title=TEXT(stored=True),              # Lưu và lập chỉ mục title
    genre=TEXT(stored=True),              # Lưu và lập chỉ mục genre
    author=TEXT(stored=True),             # Lưu và lập chỉ mục author
    publisher=TEXT(stored=True)           # Lưu và lập chỉ mục publisher
)

# Tạo thư mục lưu chỉ mục nếu chưa có và tạo chỉ mục mới
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")
    ix = create_in("indexdir", schema)
else:
    ix = open_dir("indexdir")

# Truy vấn dữ liệu từ bảng 'books'
cursor.execute("SELECT id, title, genre, author, publisher FROM books")

# Thêm dữ liệu vào chỉ mục Whoosh
writer = ix.writer()
for row in cursor:
    book_id, title, genre, author, publisher = row
    writer.add_document(id=str(book_id), title=title, genre=genre, author=author, publisher=publisher)

# Lưu các thay đổi vào chỉ mục
writer.commit()

# Đóng kết nối CSDL
conn.close()

print("Data has been successfully indexed into Whoosh.")
