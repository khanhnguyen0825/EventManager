from flask import Flask
from app.routes import auth_bp

app = Flask(
    __name__, 
    static_folder="app/static", 
    template_folder="app/templates"
)
app.secret_key = "auth-secret"

# Đăng ký Blueprint
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
