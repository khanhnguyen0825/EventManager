# run.py trong public_service
from flask import Flask
from app.routes import public_bp

app = Flask(
    __name__,
    static_folder="app/static",
    template_folder="app/templates"
)
app.secret_key = "public-secret"

# Đăng ký route cho public
app.register_blueprint(public_bp)

if __name__ == "__main__":
    app.run(port=5004, debug=True)
