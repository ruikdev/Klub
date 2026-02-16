from flask import Blueprint

def register_blueprints(app):
    """Enregistrer tous les blueprints"""
    from routes.devoirs import devoirs_bp
    from routes.chat import chat_bp
    
    app.register_blueprint(devoirs_bp)
    app.register_blueprint(chat_bp)
