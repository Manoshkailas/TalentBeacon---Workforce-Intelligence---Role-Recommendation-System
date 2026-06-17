import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, redirect, url_for
from dotenv import load_dotenv

load_dotenv()

from backend.extensions import db, jwt, bcrypt, cors, ma
from backend.config import config


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'templates'),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'static'),
    )

    # Load config
    app.config.from_object(config.get(config_name, config['default']))

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, origins='*', supports_credentials=True)
    ma.init_app(app)

    # Register blueprints
    from backend.auth.routes import auth_bp
    from backend.employees.routes import employees_bp
    from backend.skills.routes import skills_bp
    from backend.roles.routes import roles_bp
    from backend.matching.routes import matching_bp
    from backend.gap_analysis.routes import gap_bp
    from backend.learning.routes import learning_bp
    from backend.career.routes import career_bp
    from backend.readiness.routes import readiness_bp
    from backend.projects.routes import projects_bp
    from backend.reports.routes import reports_bp
    from backend.dashboards.routes import dashboards_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(employees_bp, url_prefix='/api/employees')
    app.register_blueprint(skills_bp, url_prefix='/api/skills')
    app.register_blueprint(roles_bp, url_prefix='/api/roles')
    app.register_blueprint(matching_bp, url_prefix='/api')
    app.register_blueprint(gap_bp, url_prefix='/api')
    app.register_blueprint(learning_bp, url_prefix='/api')
    app.register_blueprint(career_bp, url_prefix='/api')
    app.register_blueprint(readiness_bp, url_prefix='/api')
    app.register_blueprint(projects_bp, url_prefix='/api')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(dashboards_bp, url_prefix='')

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token has expired', 'code': 'token_expired'}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'error': 'Invalid token', 'code': 'invalid_token'}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'error': 'Authorization required', 'code': 'authorization_required'}, 401

    # Root redirect
    @app.route('/')
    def index():
        return redirect(url_for('dashboards.login_page'))

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app
