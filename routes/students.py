from flask import Blueprint, request, jsonify
from db.students import get_db_connection
from auth.jwt_utils import token_required  # Import the token_required decorator

bp = Blueprint('students', __name__)

@bp.route('/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@bp.route('/students', methods=['POST'])
def add_student():
    data = request.json
    conn = get_db_connection()
    conn.execute('INSERT INTO students (name, image_path, classe) VALUES (?, ?, ?)',
                 (data['name'], data['image_path'], data['classe']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Étudiant ajouté'})

@bp.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.json
    conn = get_db_connection()
    conn.execute('UPDATE students SET name=?, image_path=?, classe=? WHERE id=?',
                 (data['name'], data['image_path'], data['classe'], id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Étudiant modifié'})

@bp.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Étudiant supprimé'})

# GET COUNT OF STUDENTS (admin only, protected)
@bp.route('/students/count', methods=['GET'])
@token_required  # Protect this endpoint
def get_student_count(current_user):
    if current_user['role'] != 'admin':  # Check if the user is an admin
        return jsonify({'error': 'Access denied'}), 403

    conn = get_db_connection()
    
    # Count total students
    student_count = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'student_count': student_count
    })
