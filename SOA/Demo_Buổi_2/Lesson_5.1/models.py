from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', back_populates='author')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', back_populates='category')

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(50))
    published_year = db.Column(db.Integer)
    status = db.Column(db.String(20), default='available')

    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    author = db.relationship('Author', back_populates='books')
    category = db.relationship('Category', back_populates='books')

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    borrow_date = db.Column(db.Date)
    return_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='borrowing')

    book = db.relationship('Book')

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

        # Seed sample data nếu DB trống 
        if not Author.query.first():
            # Tác giả
            a1 = Author(name="Nguyễn Nhật Ánh")
            a2 = Author(name="J.K. Rowling")
            a3 = Author(name="Dan Brown")
            a4 = Author(name="Haruki Murakami")

            # Thể loại
            c1 = Category(name="Thiếu nhi")
            c2 = Category(name="Fantasy")
            c3 = Category(name="Trinh thám")
            c4 = Category(name="Văn học Nhật Bản")

            # Danh sách sách demo
            books = [
                Book(title="Mắt Biếc", isbn="VN001", published_year=1990, author=a1, category=c1),
                Book(title="Cho tôi xin một vé đi tuổi thơ", isbn="VN002", published_year=2008, author=a1, category=c1),
                Book(title="Cô gái đến từ hôm qua", isbn="VN003", published_year=1995, author=a1, category=c1),
                Book(title="Ngồi khóc trên cây", isbn="VN004", published_year=2013, author=a1, category=c1),
                Book(title="Hạ đỏ", isbn="VN005", published_year=1994, author=a1, category=c1),

                Book(title="Harry Potter và Hòn đá Phù thủy", isbn="EN001", published_year=1997, author=a2, category=c2),
                Book(title="Harry Potter và Phòng chứa bí mật", isbn="EN002", published_year=1998, author=a2, category=c2),
                Book(title="Harry Potter và Tên tù nhân ngục Azkaban", isbn="EN003", published_year=1999, author=a2, category=c2),
                Book(title="Harry Potter và Chiếc cốc lửa", isbn="EN004", published_year=2000, author=a2, category=c2),
                Book(title="Harry Potter và Hội Phượng hoàng", isbn="EN005", published_year=2003, author=a2, category=c2),

                Book(title="Mật mã Da Vinci", isbn="EN006", published_year=2003, author=a3, category=c3),
                Book(title="Thiên thần và Ác quỷ", isbn="EN007", published_year=2000, author=a3, category=c3),
                Book(title="Biểu tượng thất truyền", isbn="EN008", published_year=2009, author=a3, category=c3),
                Book(title="Nguồn cội", isbn="EN009", published_year=2017, author=a3, category=c3),
                Book(title="Pháo đài số", isbn="EN010", published_year=1998, author=a3, category=c3),

            ]

            db.session.add_all([a1, a2, a3, a4, c1, c2, c3, c4] + books)
            db.session.commit()


            
