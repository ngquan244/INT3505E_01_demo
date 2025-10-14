from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import date
from models import db, Book, Author, Category, Borrow, init_db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
init_db(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/books')
def get_books():
    q = request.args.get('q', type=str)
    category_id = request.args.get('category_id', type=int)
    author_id = request.args.get('author_id', type=int)
    status = request.args.get('status', type=str)
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=5, type=int)

    query = Book.query.join(Author).join(Category)

    if q:
        like = f"%{q}%"
        query = query.filter(or_(Book.title.ilike(like), Author.name.ilike(like), Book.isbn.ilike(like)))
    if category_id:
        query = query.filter(Book.category_id == category_id)
    if author_id:
        query = query.filter(Book.author_id == author_id)
    if status:
        query = query.filter(Book.status == status)

    total = query.count()
    items = query.order_by(Book.id).offset((page-1)*limit).limit(limit).all()

    data = [{
        'id': b.id,
        'title': b.title,
        'author': b.author.name,
        'category': b.category.name,
        'published_year': b.published_year,
        'status': b.status
    } for b in items]

    return jsonify({
        'page': page,
        'limit': limit,
        'total': total,
        'total_pages': (total + limit - 1)//limit,
        'items': data
    })

@app.route('/api/borrow', methods=['POST'])
def borrow_book():
    body = request.get_json() or {}
    user_id = body.get('user_id', 'guest')
    book_id = body.get('book_id')
    if not book_id:
        return jsonify({'error': 'book_id required'}), 400
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'book not found'}), 404
    if book.status != 'available':
        return jsonify({'error': 'book not available'}), 400

    borrow = Borrow(user_id=user_id, book_id=book_id, borrow_date=date.today())
    book.status = 'borrowed'
    db.session.add(borrow)
    db.session.commit()
    return jsonify({'message': f'Đã mượn "{book.title}"', 'borrow_id': borrow.id})

@app.route('/api/return', methods=['POST'])
def return_book():
    body = request.get_json() or {}
    borrow_id = body.get('borrow_id')
    if not borrow_id:
        return jsonify({'error': 'borrow_id required'}), 400
    borrow = Borrow.query.get(borrow_id)
    if not borrow:
        return jsonify({'error': 'borrow not found'}), 404
    if borrow.status != 'borrowing':
        return jsonify({'error': 'already returned'}), 400
    borrow.status = 'returned'
    borrow.return_date = date.today()
    borrow.book.status = 'available'
    db.session.commit()
    return jsonify({'message': f'Đã trả "{borrow.book.title}"'})

if __name__ == '__main__':
    app.run(debug=True)
