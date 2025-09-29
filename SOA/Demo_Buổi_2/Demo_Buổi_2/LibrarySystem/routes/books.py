from flask import Blueprint, jsonify, request
from models import books
from config import CACHE_TIMEOUT


books_bp = Blueprint("books_bp", __name__)


@books_bp.route("/", methods=["GET"])
def get_books():
    response = jsonify(books)
    # Nguyên tắc Cacheable
    response.headers["Cache-Control"] = f"public, max-age={CACHE_TIMEOUT}"
    return response


@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = books.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book)


@books_bp.route("/", methods=["POST"])
def add_book():
    data = request.json
    new_id = max(books.keys()) + 1
    books[new_id] = {"title": data["title"], "author": data["author"], "available": True}
    return jsonify({new_id: books[new_id]}), 201


@books_bp.route("/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    if book_id not in books:
        return jsonify({"error": "Book not found"}), 404
    data = request.json
    books[book_id].update(data)
    return jsonify({book_id: books[book_id]})


@books_bp.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    if book_id not in books:
        return jsonify({"error": "Book not found"}), 404
    deleted = books.pop(book_id)
    return jsonify({"deleted": deleted})


