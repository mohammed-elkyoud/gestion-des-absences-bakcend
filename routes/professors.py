from flask import Blueprint, request, jsonify
from db.database import get_db_connection
import bcrypt
from auth.jwt_utils import generate_token, decode_token

bp = Blueprint('professors', __name__)

ADMIN_API_KEY = 'your_admin_api_key_here'  # Change this to a strong secret key

def check_admin_auth():
    """Check for valid admin API key or JWT admin token"""
    api_key = request.headers.get('API-Key')
    if api_key == ADMIN_API_KEY:
        return True
    
    # For JWT auth
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split()[1]
            current_user = decode_token(token)
            return current_user.get('role') == 'admin'
        except:
            return False
    return False

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
def get_all():
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized - Admin access required'}), 403

    conn = get_db_connection()
    profs = conn.execute('SELECT * FROM professors').fetchall()
    conn.close()
    
    return jsonify([{
        'id': p['id'],
        'firstName': p['firstName'],
        'lastName': p['lastName'],
        'gmailAcademique': p['gmailAcademique'],
        'role': p['role'],
        'matiere': p['matiere'],
        'classes': p['classes']
    } for p in profs])

# GET SINGLE PROFESSOR (protected)
@bp.route('/professors/<int:id>', methods=['GET'])
def get_professor(id):
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized - Admin access required'}), 403

    conn = get_db_connection()
    prof = conn.execute('SELECT * FROM professors WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if prof:
        return jsonify({
            'id': prof['id'],
            'firstName': prof['firstName'],
            'lastName': prof['lastName'],
            'gmailAcademique': prof['gmailAcademique'],
            'role': prof['role'],
            'matiere': prof['matiere'],
            'classes': prof['classes']
        })
    else:
        return jsonify({'error': 'Professor not found'}), 404

# ADD PROFESSOR (admin only)
@bp.route('/professors', methods=['POST'])
def add_professor():
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized - Admin access required'}), 403

    data = request.json
    # Validate required fields
    required_fields = ['firstName', 'lastName', 'gmailAcademique', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        password = data['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO professors 
            (firstName, lastName, matiere, gmailAcademique, classes, password, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['firstName'],
            data['lastName'],
            data.get('matiere', ''),
            data['gmailAcademique'],
            data.get('classes', ''),
            hashed_password,
            data.get('role', 'professor')  # Default to 'professor' if not provided
        ))
        conn.commit()
        professor_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()

        return jsonify({
            'message': 'Professor added successfully',
            'id': professor_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# UPDATE PROFESSOR (admin only)
@bp.route('/professors/<int:id>', methods=['PUT'])
def update(id):
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized - Admin access required'}), 403

    data = request.json
    conn = get_db_connection()

    # Prepare the update query
    update_query = '''
        UPDATE professors SET firstName=?, lastName=?, matiere=?, gmailAcademique=?, classes=?, role=?
    '''
    params = [
        data['firstName'],
        data['lastName'],
        data['matiere'],
        data['gmailAcademique'],
        data['classes'],
        data.get('role', 'professor'),  # Default to 'professor' if not provided
    ]

    # Check if password is provided
    if 'password' in data and data['password']:
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        update_query += ', password=?'
        params.append(hashed_password)

    # Add the ID to the parameters for the WHERE clause
    params.append(id)
    update_query += ' WHERE id=?'

    # Execute the update query
    conn.execute(update_query, params)
    conn.commit()
    conn.close()

    return jsonify({'message': 'Professor updated'})

# DELETE PROFESSOR (admin only)
@bp.route('/professors/<int:id>', methods=['DELETE'])
def delete(id):
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized - Admin access required'}), 403

    conn = get_db_connection()
    conn.execute('DELETE FROM professors WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Professor deleted'})

# GET COUNT OF PROFESSORS (admin only)
@bp.route('/professors/count', methods=['GET'])
def get_professor_count():
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized - Admin access required'}), 403

    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM professors').fetchone()[0]
    conn.close()
    
    return jsonify({'count': count})
