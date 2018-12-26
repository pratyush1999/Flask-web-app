from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'users.login'


def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)
	db.init_app(app)
	migrate.init_app(app, db)
	login.init_app(app)

	from app.users.routes import users
	from app.posts.routes import posts
	from app.main.routes import main

	app.register_blueprint(users)
	app.register_blueprint(posts)
	app.register_blueprint(main)

	return app
