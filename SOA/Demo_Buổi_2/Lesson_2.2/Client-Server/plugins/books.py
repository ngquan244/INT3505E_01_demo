from flask import jsonify, request, url_for

BOOKS = [
    {"id": 1, "title": "Lập trình Python", "available": True},
    {"id": 2, "title": "Trí tuệ nhân tạo cơ bản", "available": True},
    {"id": 3, "title": "Cấu trúc dữ liệu & Giải thuật", "available": False},
]

def register(app):
    @app.route("/api/books")
    def get_books():
        books_with_links = []
        for b in BOOKS:
            book = b.copy()
            book["type"] = "book"
            book["links"] = {
                "self": url_for("get_books"),
                "borrow": url_for("borrow_book"),
                "return": url_for("return_book"),
            }
            books_with_links.append(book)
        return jsonify(books_with_links)

    @app.route("/api/borrow", methods=["POST"])
    def borrow_book():
        data = request.json
        token = data.get("token")
        book_id = data.get("book_id")

        if token != "demo_token_123":
            return jsonify({"error": "Unauthorized"}), 401

        for book in BOOKS:
            if book["id"] == book_id:
                if not book["available"]:
                    return jsonify({"message": "Sách đã được mượn"}), 400
                book["available"] = False
                return jsonify({"message": f"Đã mượn '{book['title']}'"})
        return jsonify({"message": "Không tìm thấy sách"}), 404

    @app.route("/api/return", methods=["POST"])
    def return_book():
        data = request.json
        token = data.get("token")
        book_id = data.get("book_id")

        if token != "demo_token_123":
            return jsonify({"error": "Unauthorized"}), 401

        for book in BOOKS:
            if book["id"] == book_id:
                book["available"] = True
                return jsonify({"message": f"Đã trả '{book['title']}'"})
        return jsonify({"message": "Không tìm thấy sách"}), 404
