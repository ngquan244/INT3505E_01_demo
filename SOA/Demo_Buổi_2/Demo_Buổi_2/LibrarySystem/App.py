# Server trong nguyên tắc 1: Client-Server
from flask import Flask
from routes.books import books_bp
from routes.borrow import borrow_bp
from routes.system import system_bp
from utils.auth import auth_middleware


def create_app():
    app = Flask(__name__)

    # Middleware stateless auth
    app.before_request(auth_middleware)

    # Register blueprints (module routes)
    app.register_blueprint(books_bp, url_prefix="/books")
    app.register_blueprint(borrow_bp, url_prefix="/library")
    app.register_blueprint(system_bp, url_prefix="/system")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
