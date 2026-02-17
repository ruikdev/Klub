from flask import Blueprint, jsonify
from utils import get_notes

notes_bp = Blueprint('notes', __name__, url_prefix='/api')

@notes_bp.route('/notes', methods=['GET'])
def notes():
    """Récupérer tous les notes avec leurs détails"""
    notes_data, error = get_notes()
    
    if error:
        return jsonify(error=error), 500
    
    return jsonify(notes_data), 200
