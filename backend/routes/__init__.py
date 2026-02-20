from flask import Blueprint

def register_blueprints(app):
    """Enregistrer tous les blueprints"""
    from routes.devoirs import devoirs_bp
    from routes.chat import chat_bp
    from routes.notes import notes_bp
    from routes.cours import cours_bp
    from routes.ocr import ocr_bp
    
    app.register_blueprint(devoirs_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(cours_bp)
    app.register_blueprint(ocr_bp)
    app.register_blueprint(flashCard_bp)