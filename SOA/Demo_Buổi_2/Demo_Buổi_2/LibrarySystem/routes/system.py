from flask import Blueprint, jsonify, request, Response

system_bp = Blueprint("system_bp", __name__)


@system_bp.route("/check-layer", methods=["GET"])
def check_layer():
    return jsonify({"via": request.headers.get("Via", "Direct Server")})


@system_bp.route("/script", methods=["GET"])
def send_script():
    js_code = "console.log('Hello World :3');"
    return Response(js_code, mimetype="application/javascript")
