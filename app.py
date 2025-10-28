from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
from datetime import datetime
import sqlite3
from werkzeug.utils import secure_filename
import json

# استيراد الدوال من ملف توليد PDF الموجود
from report_generator_system import generate_report_pdf

app = Flask(__name__)
CORS(app)  # للسماح بالطلبات من النموذج المحلي

# Serve the frontend form and its static assets from the `form/` directory
@app.route('/')
def index():
    return send_file(os.path.join('form', 'index.html'))


@app.route('/<path:filename>')
def serve_static(filename):
    # Prevent accidental shadowing of API routes
    if filename.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    file_path = os.path.join('form', filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({'error': 'Not found'}), 404

# إعدادات المجلدات والملفات
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
DATABASE = 'reports.db'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# إنشاء قاعدة البيانات وجدول السجلات
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_name TEXT NOT NULL,
            execution_date TEXT NOT NULL,
            executor_name TEXT NOT NULL,
            location TEXT NOT NULL,
            target_group TEXT NOT NULL,
            images TEXT NOT NULL,
            pdf_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# معالجة رفع النموذج وتوليد PDF
@app.route('/api/submit', methods=['POST'])
def submit_form():
    try:
        # استلام البيانات
        data = {
            'activity_name': request.form['activityName'],
            'execution_date': request.form['executionDate'],
            'executor_name': request.form['executorName'],
            'location': request.form['location'],
            'target_group': request.form['targetGroup']
        }
        
        # حفظ الصور
        images = request.files.getlist('images')
        image_paths = []
        
        for img in images:
            if img:
                filename = secure_filename(img.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                img.save(filepath)
                image_paths.append(filepath)
        
        if len(image_paths) != 4:
            return jsonify({'error': 'يجب تحديد أربع صور بالضبط'}), 400
        
        # توليد PDF
        pdf_filename = f"{data['activity_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(REPORTS_FOLDER, pdf_filename)
        
        generate_report_pdf(
            activity_name=data['activity_name'],
            execution_date=data['execution_date'],
            executor_name=data['executor_name'],
            place=data['location'],
            target_group=data['target_group'],
            evidence_paths=image_paths,
            output_path=pdf_path
        )
        
        # حفظ في قاعدة البيانات
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO reports 
            (activity_name, execution_date, executor_name, location, target_group, images, pdf_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['activity_name'],
            data['execution_date'],
            data['executor_name'],
            data['location'],
            data['target_group'],
            json.dumps(image_paths),
            pdf_path
        ))
        conn.commit()
        report_id = c.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء التقرير بنجاح',
            'report_id': report_id,
            'pdf_url': f'/api/reports/{report_id}/pdf'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# استرجاع PDF محدد
@app.route('/api/reports/<int:report_id>/pdf')
def get_report_pdf(report_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT pdf_path FROM reports WHERE id = ?', (report_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return send_file(result[0], mimetype='application/pdf')
    return jsonify({'error': 'لم يتم العثور على التقرير'}), 404

# استرجاع قائمة التقارير السابقة
@app.route('/api/reports')
def get_reports():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT id, activity_name, execution_date, executor_name, created_at 
        FROM reports 
        ORDER BY created_at DESC
    ''')
    reports = [{
        'id': row[0],
        'activity_name': row[1],
        'execution_date': row[2],
        'executor_name': row[3],
        'created_at': row[4]
    } for row in c.fetchall()]
    conn.close()
    
    return jsonify(reports)

if __name__ == '__main__':
    app.run(debug=True, port=5000)