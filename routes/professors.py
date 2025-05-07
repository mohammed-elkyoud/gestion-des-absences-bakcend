from flask import Blueprint, request, jsonify
from db.database import get_db_connection
import bcrypt

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
        return jsonify({
            'message': 'Login successful',
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

# GET ALL PROFESSORS
@bp.route('/professors', methods=['GET'])
def get_all():
    conn = get_db_connection()
    profs = conn.execute('SELECT * FROM professors').fetchall()
    conn.close()
    return jsonify([dict(p) for p in profs])

# UPDATE PROFESSOR (admin only)
@bp.route('/professors/<int:id>', methods=['PUT'])
def update(id):
    data = request.json

    # Optional: simulate admin check
    if data.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized – admin only'}), 403

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

# DELETE PROFESSOR (admin only)
@bp.route('/professors/<int:id>', methods=['DELETE'])
def delete(id):
    data = request.json
    if data.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized – admin only'}), 403

    conn = get_db_connection()
    conn.execute('DELETE FROM professors WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Professor deleted'})
