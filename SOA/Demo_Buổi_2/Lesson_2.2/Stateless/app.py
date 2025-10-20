from flask import Flask, request, jsonify, render_template
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

SWAGGER_URL = "/swagger"
API_URL = "/static/openapi.yaml"
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Giả lập dữ liệu
BOOKS = [
    {"id": 1, "title": "Lập trình Python", "available": True},
    {"id": 2, "title": "Trí tuệ nhân tạo cơ bản", "available": True},
    {"id": 3, "title": "Cấu trúc dữ liệu & Giải thuật", "available": False},
]

# API: lấy danh sách sách
@app.route("/api/books", methods=["GET"])
def get_books():
    return jsonify(BOOKS)

# API: mượn sách (Stateless: yêu cầu phải gửi token + id sách)
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

# API: trả sách
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

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
