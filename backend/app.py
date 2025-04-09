#!/usr/bin/env python3
"""
LocalFlix Backend - Main Flask Application
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_cors import CORS

def create_app(test_config=None):
    """Create and configure the Flask application."""
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Enable CORS for frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Load default configuration
    app.config.from_object('config.Config')
    
    # Load instance configuration, if it exists
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Ensure the logs folder exists
    try:
        os.makedirs('logs', exist_ok=True)
    except OSError:
        pass
    
    # Configure logging
    handler = RotatingFileHandler('logs/localflix.log', maxBytes=10485760, backupCount=5)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('LocalFlix backend starting up')
    
    # Register routes
    from routes.api import api_bp
    from routes.stream import stream_bp
    
    app.register_blueprint(api_bp)
    app.register_blueprint(stream_bp)
    
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({"status": "healthy", "service": "localflix-backend"})
    
    return app

app = create_app()

if __name__ == '__main__':
    # Run the app
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', False)
    
    app.run(host=host, port=port, debug=debug)
