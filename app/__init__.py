import os

from dotenv import load_dotenv
from flask import Flask
from flask_admin.menu import MenuLink
from flask_login import LoginManager
from flask_mail import Mail
from flask_admin import Admin

from config import Config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = Flask(__name__, static_folder='static', static_url_path='')
app.config.from_object(Config)
db = SQLAlchemy(app=app)
migrate = Migrate(app, db, render_as_batch=True)
bootstrap = Bootstrap(app)
csrf = CSRFProtect()
csrf.init_app(app)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)

from app import views, models
# from app.models import *
# from app.admin import *
# admin = Admin(app, name="Workshop", index_view=MyAdminView())
# admin.add_view(CompanyAdminView(Company, db.session))
# admin.add_view(MyModelView(CompanyConfig, db.session))
# admin.add_view(MyModelView(Tariff, db.session))
# admin.add_view(UserAdminView(User, db.session))
# admin.add_view(MyModelView(Role, db.session))
# admin.add_view(MyModelView(Permission, db.session))
# with app.test_request_context():
#     admin.add_link(MenuLink(name='Go to site', url=url_for('index')))
