from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

DATABASE = 'files.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            filename TEXT NOT NULL,
            filedata BLOB NOT NULL
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
        file = request.files['file']

        if file:
            filename = secure_filename(file.filename)
            filedata = file.read()
            conn.execute('INSERT INTO files (filename, filedata) VALUES (?, ?)', (filename, filedata))
            conn.commit()

    files = conn.execute('SELECT * FROM files').fetchall()
    conn.close()
    return render_template('single_file.html', files=files)

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM files WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/download/<int:id>', methods=('GET',))
def download(id):
    conn = get_db_connection()
    file = conn.execute('SELECT filename, filedata FROM files WHERE id = ?', (id,)).fetchone()
    conn.close()
    return (file['filedata'], {
        'Content-Disposition': f'attachment; filename={file["filename"]}',
        'Content-Type': 'application/octet-stream'
    })

if __name__ == '__main__':
    app.run(debug=True)
