from flask import Flask, redirect, request, url_for
from flask_migrate import Migrate
from flask_login import LoginManager
from project.config import config
from flask_wtf import CSRFProtect

config = config['development']

def create_app():
    from project.extensions.dependencies import db, bcrypt

    main = Flask(__name__)
    
    main.config.from_object(config)

    # Db
    db.init_app(main)

    # Bcrypt
    bcrypt.init_app(main)

    # CSRF
    csrf = CSRFProtect()
    csrf.init_app(main)

    # Login manager
    login_manager = LoginManager()
    login_manager.init_app(main)

    # Login manager userloader callback
    from project.models.users import User, AnonymousUser

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(uid)
    
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        # Check if the user is trying to access an admin route
        if '/admin/' in request.path:
            return redirect(url_for('admin.index'))
        # Otherwise, redirect to the normal user login
        return redirect(url_for('app.signin'))
    
    # Login manager anonymous user class
    login_manager.anonymous_user = AnonymousUser

    # Import blueprints
    from project.app.routes import app
    from project.admin.routes import admin


    # Register blueprints
    main.register_blueprint(app, url_prefix='/')
    main.register_blueprint(admin, url_prefix='/admin')
    
    with main.app_context():
        db.create_all()

    migrate = Migrate(main, db)
    return main