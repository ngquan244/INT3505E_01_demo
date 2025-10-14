from flask import Flask, request, jsonify, render_template, make_response
import time

app = Flask(__name__)

# Dữ liệu giả lập
BOOKS = [
    {"id": 1, "title": "Lập trình Python", "available": True},
    {"id": 2, "title": "Trí tuệ nhân tạo cơ bản", "available": True},
    {"id": 3, "title": "Cấu trúc dữ liệu & Giải thuật", "available": False},
]


# API: LẤY DANH SÁCH SÁCH (Cacheable)
@app.route("/api/books", methods=["GET"])
def get_books():
    resp = make_response(jsonify(BOOKS))
    resp.headers["Cache-Control"] = "no-store"  # Không cache
    resp.headers["X-Server-Time"] = time.strftime("%H:%M:%S")
    return resp



# API: MƯỢN SÁCH (Stateless: mỗi request phải gửi token)
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

# API: lấy thông tin 1 sách (Uniform Interface)
@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if not book:
        return jsonify({"message": "Không tìm thấy sách"}), 404
    return jsonify(book)

# API : TRẢ SÁCH
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


# TRANG GIAO DIỆN
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
