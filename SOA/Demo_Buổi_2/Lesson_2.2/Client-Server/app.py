from flask import Flask, request, jsonify, render_template, url_for

app = Flask(__name__)

# Dư liệu giả lập
BOOKS = [
    {"id": 1, "title": "Lập trình Python", "available": True},
    {"id": 2, "title": "Trí tuệ nhân tạo cơ bản", "available": True},
    {"id": 3, "title": "Cấu trúc dữ liệu & Giải thuật", "available": False},
]


# API: LẤY DANH SÁCH SÁCH
@app.route("/api/books", methods=["GET"])
def get_books():
    books_with_links = []
    for b in BOOKS:
        book = b.copy()
        book["type"] = "book"
        book["links"] = {
            "self": url_for("get_book", book_id=b["id"]),
            "borrow": url_for("borrow_book"),
            "return": url_for("return_book"),
        }
        books_with_links.append(book)
    return jsonify(books_with_links)


# API: LẤY THÔNG TIN 1 SÁCH
@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    for b in BOOKS:
        if b["id"] == book_id:
            b_copy = b.copy()
            b_copy["type"] = "book"
            b_copy["links"] = {
                "self": url_for("get_book", book_id=book_id),
                "borrow": url_for("borrow_book"),
                "return": url_for("return_book"),
            }
            return jsonify(b_copy)
    return jsonify({"error": "Không tìm thấy sách"}), 404


# API: MƯỢN SÁCH 
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
            return jsonify({
                "message": f"Đã mượn '{book['title']}'",
                "links": {"return": url_for("return_book")}
            })

    return jsonify({"message": "Không tìm thấy sách"}), 404


# API: TRẢ SÁCH 
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
            return jsonify({
                "message": f"Đã trả '{book['title']}'",
                "links": {"borrow": url_for("borrow_book")}
            })

    return jsonify({"message": "Không tìm thấy sách"}), 404


# GIAO DIỆN NGƯỜI DÙNG 
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
