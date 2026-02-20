from flask import Blueprint, jsonify, request
import os


flashCard_bp = Blueprint('flashCard', __name__, url_prefix='/api')

@flashCard_bp.route('/flash-cards', methods=['GET'])