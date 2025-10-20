from flask import jsonify

AUTHORS = [
    {"id": 1, "name": "Nguyễn Nhật Ánh"},
    {"id": 2, "name": "J.K. Rowling"},
]

def register(app):
    @app.route("/api/authors")
    def get_authors():
        return jsonify(AUTHORS)
