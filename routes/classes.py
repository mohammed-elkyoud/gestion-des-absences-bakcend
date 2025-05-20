import os
import fitz  # PyMuPDF
import re
from flask import Blueprint, request, jsonify
from db.database import get_db_connection

bp = Blueprint('classes', __name__)


# ✅ Fonction d'extraction depuis PDF structuré en tableau
def extract_names_from_pdf(pdf_path):
    names = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            blocks = page.get_text("blocks")  # blocs = (x0, y0, x1, y1, "text", block_no, block_type)
            for block in blocks:
                line = block[4].strip()
                parts = line.split()
                if len(parts) >= 3 and parts[0].isdigit() and len(parts[0]) == 7:
                    nom = parts[1]
                    prenom_parts = parts[2:]
                    # On enlève les 'X', 'Groupe', etc.
                    prenom_clean = " ".join([
                        p for p in prenom_parts
                        if p.upper() != 'X' and not p.lower().startswith("groupe")
                    ])
                    if nom and prenom_clean:
                        names.append(f"{nom} {prenom_clean}")
    return names

# 🔁 GET : Récupérer toutes les classes
@bp.route('/classes', methods=['GET'])
def get_classes():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM classes').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

# ➕ POST : Créer une classe manuellement
@bp.route('/classes', methods=['POST'])
def create_class():
    data = request.json
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO classes (filiere, liste_des_etudiants) VALUES (?, ?)',
        (data['filiere'], data['liste_des_etudiants'])
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Classe créée'}), 201

# 🆙 PUT : Modifier une classe
@bp.route('/classes/<int:id>', methods=['PUT'])
def update_class(id):
    data = request.json
    conn = get_db_connection()
    conn.execute(
        'UPDATE classes SET filiere=?, liste_des_etudiants=? WHERE id=?',
        (data['filiere'], data['liste_des_etudiants'], id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Classe mise à jour'})

# ❌ DELETE : Supprimer une classe
@bp.route('/classes/<int:id>', methods=['DELETE'])
def delete_class(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM classes WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Classe supprimée'})

# 📥 POST : Importer PDF et créer la classe automatiquement
@bp.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    print("Upload PDF endpoint reached")  # Debugging line
    if 'file' not in request.files or 'filiere' not in request.form:
        print("Missing file or filiere")  # Debugging line
        return jsonify({'error': 'PDF file and filiere are required'}), 400

    file = request.files['file']
    filiere = request.form['filiere']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Sauvegarde temporaire
    os.makedirs("tmp", exist_ok=True)
    filepath = os.path.join("tmp", file.filename)
    file.save(filepath)

    try:
        names = extract_names_from_pdf(filepath)

        if not names:
            return jsonify({'error': 'Aucun nom extrait du PDF'}), 400

        students_str = "; ".join(names)

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO classes (filiere, liste_des_etudiants) VALUES (?, ?)',
            (filiere, students_str)
        )
        conn.commit()
        conn.close()

        os.remove(filepath)
        return jsonify(names), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/process-attendance', methods=['POST'])
def process_attendance():
    data = request.json
    class_id = data['class_id']
    recognized_names = data['recognized_names']
    
    conn = get_db_connection()
    
    # Get the class student list
    class_data = conn.execute('SELECT liste_des_etudiants FROM classes WHERE id = ?', (class_id,)).fetchone()
    if not class_data:
        return jsonify({'error': 'Class not found'}), 404
    
    # Parse student list (assuming format "Name1; Name2; ...")
    all_students = [name.strip() for name in class_data['liste_des_etudiants'].split(';')]
    
    # Process attendance
    present_students = []
    unknown_students = []
    
    for name in recognized_names:
        if name == 'Unknown':
            unknown_students.append(name)
        elif name in all_students:
            present_students.append(name)
    
    absent_students = [student for student in all_students if student not in present_students]
    
    # Save to attendance log (you'll need to create this table)
    conn.execute(
        'INSERT INTO attendance_log (class_id, present_students, absent_students, unknown_students) '
        'VALUES (?, ?, ?, ?)',
        (class_id, ';'.join(present_students), ';'.join(absent_students), ';'.join(unknown_students))
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        'present': present_students,
        'absent': absent_students,
        'unknown': unknown_students
    })