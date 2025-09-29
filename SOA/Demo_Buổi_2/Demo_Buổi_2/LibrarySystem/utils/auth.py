from flask import request, jsonify
from config import SECRET_TOKEN


def auth_middleware():
    # Check stateless authentication via Bearer token
    if request.endpoint == "system_bp.send_script":
        return

    # Nguyên tắc 2: Stateless, không lưu trạng thái phiên
    token = request.headers.get("Authorization")
    if not token or token != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
