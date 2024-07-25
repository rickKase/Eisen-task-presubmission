from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

DATABASE = 'submissions.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create submissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                uploader TEXT NOT NULL
            )
        ''')

        # Create files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                submission_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                filedata BLOB NOT NULL,
                FOREIGN KEY(submission_id) REFERENCES submissions(id)
            )
        ''')

        conn.commit()
        conn.close()

with app.app_context():
    init_db()

@app.route('/', methods=('GET', 'POST'))
def index():
    conn = get_db_connection()

    if request.method == 'POST':
        uploader = request.form.get('uploader')
        files = request.files.getlist('file')

        if files and uploader:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO submissions (timestamp, uploader) VALUES (?, ?)', (timestamp, uploader))
            submission_id = cursor.lastrowid

            for file in files:
                filename = secure_filename(file.filename)
                filedata = file.read()
                cursor.execute('INSERT INTO files (submission_id, filename, filedata) VALUES (?, ?, ?)', 
                               (submission_id, filename, filedata))
            
            conn.commit()

    query = '''
    SELECT submissions.id as submission_id, submissions.timestamp, submissions.uploader, files.id as file_id, files.filename
    FROM submissions
    JOIN files ON submissions.id = files.submission_id
    '''
    rows = conn.execute(query).fetchall()
    conn.close()
    submissions = {}
    for row in rows:
        submission_id = row['submission_id']
        if submission_id not in submissions:
            submissions[submission_id] = {
                'timestamp': row['timestamp'],
                'uploader': row['uploader'],
                'files': []
            }
        submissions[submission_id]['files'].append({
            'file_id': row['file_id'],
            'filename': row['filename']
        })

    return render_template('multi_file.html', submissions=submissions)

@app.route('/delete/<int:submission_id>', methods=('POST',))
def delete(submission_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM files WHERE submission_id = ?', (submission_id,))
    conn.execute('DELETE FROM submissions WHERE id = ?', (submission_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete_file/<int:file_id>', methods=('POST',))
def delete_file(file_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM files WHERE id = ?', (file_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/download/<int:file_id>', methods=('GET',))
def download(file_id):
    conn = get_db_connection()
    file = conn.execute('SELECT filename, filedata FROM files WHERE id = ?', (file_id,)).fetchone()
    conn.close()
    return (file['filedata'], {
        'Content-Disposition': f'attachment; filename={file["filename"]}',
        'Content-Type': 'application/octet-stream'
    })

@app.route('/add_files/<int:submission_id>', methods=('POST',))
def add_files(submission_id):
    conn = get_db_connection()
    files = request.files.getlist('file')

    if files:
        cursor = conn.cursor()
        for file in files:
            filename = secure_filename(file.filename)
            filedata = file.read()
            cursor.execute('INSERT INTO files (submission_id, filename, filedata) VALUES (?, ?, ?)', 
                           (submission_id, filename, filedata))
        
        conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
