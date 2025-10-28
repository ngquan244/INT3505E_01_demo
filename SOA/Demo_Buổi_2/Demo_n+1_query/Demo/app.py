from flask import Flask, Response, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from model import Book
from flasgger import Swagger
import yaml
import json
import urllib.parse
import requests
from functools import wraps

with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

db_conf = config["database"]

params = {
    "DRIVER": f"{{{db_conf['driver']}}}",
    "SERVER": db_conf["server"],
    "DATABASE": db_conf["database"],
    "Trusted_Connection": "yes",
    "Encrypt": "yes" if db_conf.get("encrypt", False) else "no",
}

# Build connection string (dùng để kết nối và sinh model.py từ SQLcodegen)
connection_string = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(';'.join(f'{k}={v}' for k, v in params.items()))}"


engine = create_engine(connection_string, echo=True)
SessionLocal = sessionmaker(bind=engine)

app = Flask(__name__)

swagger_conf = config["swagger"]

for spec in swagger_conf.get("specs", []):
    spec["rule_filter"] = lambda rule: True
    spec["model_filter"] = lambda tag: True

swagger = Swagger(app, config=swagger_conf)

AUTH_SERVICE_URL = "http://localhost:3000/protected"

def token_required_remote(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
        if auth_header:
            if auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ")[1]
            else:
                token = auth_header 


        if not token:
            app.logger.warning("Missing Authorization header")
            return jsonify({"message": "Token is missing"}), 401

        try:
            resp = requests.get(AUTH_SERVICE_URL, headers={"Authorization": f"Bearer {token}"}, timeout=5)
        except requests.exceptions.ConnectionError:
            return jsonify({"message": "Auth service unreachable"}), 503
        except requests.exceptions.Timeout:
            return jsonify({"message": "Auth service timeout"}), 504

        if resp.status_code != 200:
            try:
                msg = resp.json().get("message", "Token invalid or expired")
            except ValueError:
                msg = "Token invalid or expired"
            return jsonify({"message": msg}), resp.status_code

        return f(*args, **kwargs)
    return decorated

@app.route("/login", methods=["POST"])
def login():
    """
    Login qua auth_service
    ---
    parameters:
      - name: username
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      200:
        description: Token trả về
        schema:
          type: object
          properties:
            accessToken:
              type: string
            refreshToken:
              type: string
    """
    username = request.form.get("username")
    password = request.form.get("password")

    try:
        resp = requests.post(
            "http://localhost:3000/login",
            json={"username": username, "password": password},
            timeout=5
        )
    except requests.exceptions.RequestException:
        return jsonify({"message": "Auth service unreachable"}), 503

    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get("Content-Type"))

# Route gây ra N+1 # Truy cập book.Author
# Query riêng cho từng row - N queries
@app.route("/books")
def get_books_nplus1():
    """
    Lấy danh sách sách (dạng N+1 query)
    ---
    responses:
      200:
        description: Danh sách sách và tác giả
    """
    session = SessionLocal()
    books = session.query(Book).all()
    result = []
    for book in books:
        result.append({
            "title": book.Title,
            "author": book.Author_.Name if book.Author_ else None
        })
    return Response(
        json.dumps(result, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )


# Solution: join luôn Author 
# Eager Loading với joinedload
@app.route("/books-solution")
def get_books_optimized():
    """
    Lấy danh sách sách (đã tối ưu bằng joinedload)
    ---
    responses:
      200:
        description: Danh sách sách với thông tin tác giả (tối ưu)
    """
    session = SessionLocal()
    books = session.query(Book).options(joinedload(Book.Author_)).all()
    result = [
        {"title": b.Title, "author": b.Author_.Name if b.Author_ else None}
        for b in books
    ]
    return Response(
        json.dumps(result, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )

@app.route("/books-jwt-remote")
@token_required_remote
def get_books_jwt_remote():
    """
    Lấy danh sách sách (bảo vệ bằng JWT remote)
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Danh sách sách với JWT kiểm tra qua Node.js auth_service
    """
    session = SessionLocal()
    books = session.query(Book).options(joinedload(Book.Author_)).all()
    result = [
        {"title": b.Title, "author": b.Author_.Name if b.Author_ else None}
        for b in books
    ]
    return Response(
        json.dumps(result, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )

@app.route("/")
def index():
    """
    Trang giới thiệu API
    ---
    responses:
      200:
        description: Danh sách endpoint của API
    """
    return Response(
        json.dumps({
            "routes": ["/books", "/books-solution", "/books-jwt-remote"],
            "swagger": swagger_conf.get("specs_route", "/swagger/"),
            "description": "Demo N+1 query issue, solution, và JWT remote auth"
        }, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )


if __name__ == "__main__":
    app.run(debug=True)
