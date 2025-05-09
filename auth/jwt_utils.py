# auth/jwt_utils.py
import jwt
import datetime
from flask import request, jsonify
from functools import wraps

SECRET_KEY = 'your_super_secret_key'
JWT_EXPIRATION = datetime.timedelta(days=7)

def generate_token(user_data):
    token = jwt.encode({
        'id': user_data['id'],
        'gmailAcademique': user_data['gmailAcademique'],
        'role': user_data['role'],
        'exp': datetime.datetime.utcnow() + JWT_EXPIRATION
    }, SECRET_KEY, algorithm='HS256')
    return token

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        if not token:
            return jsonify({'error': 'Token missing'}), 401

        decoded = decode_token(token)
        if 'error' in decoded:
            return jsonify(decoded), 401

        return f(decoded, *args, **kwargs)
    return decorated
