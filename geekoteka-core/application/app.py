from flask import Flask
from routes import geekoczelnia_bp
import os
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.secret_key = 'your_unique_and_secret_key_here'
# Rejestrujemy blueprint z routami
app.register_blueprint(geekoczelnia_bp)

if __name__ == '__main__':
    app.run(debug=True)
