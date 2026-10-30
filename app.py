import os
from flask import Flask
from flask_login import LoginManager
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ganti-dengan-string-rahasia-panjang'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'perpustakaan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100 MB

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
    
from routes import *
if __name__ == '_main_':
    with app.app_context():
        db.create_all()   #buat tabel otmts
        #render akan memberikan port otmts, kl di lptp ttp 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
