from flask import Blueprint, request, jsonify
from db.database import get_db_connection
import bcrypt
from auth.jwt_utils import generate_token, token_required

bp = Blueprint('professors', __name__)

# SIGN UP
@bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    password = data['password'].encode('utf-8')
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    role = data.get('role', 'professor')  # Default role

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO professors (firstName, lastName, matiere, gmailAcademique, classes, password, role)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['firstName'],
        data['lastName'],
        data['matiere'],
        data['gmailAcademique'],
        data['classes'],
        hashed_password,
        role
    ))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Account created successfully'}), 201

# SIGN IN
@bp.route('/signin', methods=['POST'])
def signin():
    data = request.json
    email = data['gmailAcademique']
    password = data['password'].encode('utf-8')

    conn = get_db_connection()
    prof = conn.execute('SELECT * FROM professors WHERE gmailAcademique = ?', (email,)).fetchone()
    conn.close()

    if prof and bcrypt.checkpw(password, prof['password']):
        token = generate_token({
            'id': prof['id'],
            'gmailAcademique': prof['gmailAcademique'],
            'role': prof['role']
        })
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'professor': {
                'id': prof['id'],
                'firstName': prof['firstName'],
                'lastName': prof['lastName'],
                'gmailAcademique': prof['gmailAcademique'],
                'role': prof['role']
            }
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# GET ALL PROFESSORS (protected)
@bp.route('/professors', methods=['GET'])
@token_required
def get_all(current_user):
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Access denied'}), 403

    conn = get_db_connection()
    profs = conn.execute('SELECT * FROM professors').fetchall()
    conn.close()
    return jsonify([dict(p) for p in profs])

# GET SINGLE PROFESSOR (protected)
@bp.route('/professors/<int:id>', methods=['GET'])
@token_required
def get_professor(id, current_user):
    conn = get_db_connection()
    prof = conn.execute('SELECT * FROM professors WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if prof:
        return jsonify(dict(prof))
    else:
        return jsonify({'error': 'Professor not found'}), 404

# UPDATE PROFESSOR (admin only, protected)
@bp.route('/professors/<int:id>', methods=['PUT'])
@token_required
def update(id, current_user):
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized – admin only'}), 403

    data = request.json
    conn = get_db_connection()
    conn.execute('''
        UPDATE professors SET firstName=?, lastName=?, matiere=?, gmailAcademique=?, classes=?, password=?, role=?
        WHERE id=?
    ''', (
        data['firstName'],
        data['lastName'],
        data['matiere'],
        data['gmailAcademique'],
        data['classes'],
        bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()),
        data.get('role', 'professor'),
        id
    ))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Professor updated'})

# DELETE PROFESSOR (admin only, protected)
@bp.route('/professors/<int:id>', methods=['DELETE'])
@token_required
def delete(id, current_user):
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized – admin only'}), 403

    conn = get_db_connection()
    conn.execute('DELETE FROM professors WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Professor deleted'})
