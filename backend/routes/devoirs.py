from flask import Blueprint, jsonify
from utils import get_devoirs_with_details

devoirs_bp = Blueprint('devoirs', __name__, url_prefix='/api')

@devoirs_bp.route('/devoirs', methods=['GET'])
def devoirs():
    """Récupérer tous les devoirs avec leurs détails"""
    devoirs_data, error = get_devoirs_with_details()
    
    if error:
        return jsonify(error=error), 500
    
    return jsonify(devoirs_data), 200
