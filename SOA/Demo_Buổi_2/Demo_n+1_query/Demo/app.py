from flask import Flask, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from model import Book
import yaml
import json
import urllib.parse


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

# Route gây ra N+1 # Truy cập book.Author
# Query riêng cho từng row - N queries
@app.route("/books")
def get_books_nplus1():
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
    return Response(
        json.dumps({
            "routes": ["/books", "/books-solution"],
            "description": "Demo N+1 query issue vs solution query"
        }, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )


if __name__ == "__main__":
    app.run(debug=True)
