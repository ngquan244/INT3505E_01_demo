from flask import Blueprint, jsonify
from models import books, borrowed

borrow_bp = Blueprint("borrow_bp", __name__)


@borrow_bp.route("/borrow/<int:book_id>", methods=["POST"])
def borrow_book(book_id):
    if book_id not in books:
        return jsonify({"error": "Book not found"}), 404
    if not books[book_id]["available"]:
        return jsonify({"error": "Book already borrowed"}), 400
    books[book_id]["available"] = False
    borrowed[book_id] = books[book_id]
    return jsonify({"message": "Borrowed successfully", "book": books[book_id]})


@borrow_bp.route("/return/<int:book_id>", methods=["POST"])
def return_book(book_id):
    if book_id not in borrowed:
        return jsonify({"error": "Book was not borrowed"}), 400
    books[book_id]["available"] = True
    borrowed.pop(book_id)
    return jsonify({"message": "Returned successfully", "book": books[book_id]})
