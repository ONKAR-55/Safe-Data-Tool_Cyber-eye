from flask import Flask, render_template, request, send_from_directory
import os
import pandas as pd
from cryptography.fernet import Fernet
from flask import send_from_directory

app = Flask(__name__)

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'processed')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Setup AES encryption
key = Fernet.generate_key()
cipher = Fernet(key)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    method = request.form.get('method')

    if method != 'encrypt':
        return "Only encryption method is supported for now.", 400

    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        df = pd.read_csv(filepath)

        if 'Name' not in df.columns:
            return "Missing 'Name' column in the file.", 400

        # Encrypt the 'Name' column using AES
        for col in df.columns:
            df[col] = df[col].apply(lambda x: cipher.encrypt(str(x).encode()).decode())

        # Save processed file
        processed_filename = 'processed_' + filename
        processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
        df.to_csv(processed_path, index=False)

        # Pass result to template
        return render_template('result.html', result_file=processed_filename)

    except Exception as e:
        return f"Error while processing: {str(e)}", 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
