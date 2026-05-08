from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.expenses import expenses_bp
    from routes.categories import categories_bp
    from routes.budgets import budgets_bp
    from routes.export import export_bp
    from routes.salary import salary_bp
    from routes.goals import goals_bp
    from routes.report import report_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(salary_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(report_bp)

    from flask_wtf.csrf import CSRFProtect, generate_csrf
    CSRFProtect(app)

    @app.context_processor
    def inject_globals():
        from datetime import date
        from markupsafe import Markup
        from flask_wtf.csrf import generate_csrf
        def csrf_token_input():
            return Markup(f'<input type="hidden" name="csrf_token" value="{generate_csrf()}">')
        return dict(csrf_token_input=csrf_token_input, now=date.today())

    with app.app_context():
        db.create_all()

    return app
