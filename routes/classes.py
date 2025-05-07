from flask import Blueprint, request, jsonify
from db.database import get_db_connection

bp = Blueprint('classes', __name__)

@bp.route('/classes', methods=['GET'])
def get_classes():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM classes').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@bp.route('/classes', methods=['POST'])
def create_class():
    data = request.json
    conn = get_db_connection()
    conn.execute('INSERT INTO classes (filiere, liste_des_etudiants) VALUES (?, ?)',
                 (data['filiere'], data['liste_des_etudiants']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Classe créée'})

@bp.route('/classes/<int:id>', methods=['PUT'])
def update_class(id):
    data = request.json
    conn = get_db_connection()
    conn.execute('UPDATE classes SET filiere=?, liste_des_etudiants=? WHERE id=?',
                 (data['filiere'], data['liste_des_etudiants'], id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Classe mise à jour'})

@bp.route('/classes/<int:id>', methods=['DELETE'])
def delete_class(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM classes WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Classe supprimée'})
