from flask import Flask, render_template
import importlib, pkgutil

app = Flask(__name__)

# extensible khi mở rộng bằng plugins
def load_plugins():
    package = 'plugins'
    for _, module_name, _ in pkgutil.iter_modules([package]):
        module = importlib.import_module(f'{package}.{module_name}')
        # Nếu plugin có hàm register(app), gọi nó
        if hasattr(module, "register"):
            module.register(app)

load_plugins()

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
