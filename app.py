from flask import Flask, render_template, request, send_from_directory
import os
import pandas as pd
from cryptography.fernet import Fernet, InvalidToken
from flask import send_from_directory

app = Flask(__name__)

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'processed')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    method = request.form.get('method')
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    if method == 'encrypt':
        try:
            df = pd.read_csv(filepath)

            # Setup AES encryption
            key = Fernet.generate_key()
            cipher = Fernet(key)

            # Encrypt all columns using AES
            for col in df.columns:
                df[col] = df[col].apply(lambda x: cipher.encrypt(str(x).encode()).decode())

            # Save processed file
            processed_filename = 'processed_' + filename
            processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
            df.to_csv(processed_path, index=False)

            # Pass result to template
            return render_template('result.html', result_file=processed_filename, decryption_key=key.decode())

        except Exception as e:
            return f"Error while processing: {str(e)}", 500

    elif method == 'decrypt':
        decryption_key = request.form.get('decryption_key')
        if not decryption_key:
            return "Decryption key is required", 400

        try:
            df = pd.read_csv(filepath)

            # Setup AES decryption
            cipher = Fernet(decryption_key.encode())

            # Decrypt all columns using AES
            for col in df.columns:
                df[col] = df[col].apply(lambda x: cipher.decrypt(str(x).encode()).decode())

            # Save processed file
            processed_filename = 'processed_' + filename
            processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
            df.to_csv(processed_path, index=False)

            # Pass result to template
            return render_template('result.html', result_file=processed_filename)

        except InvalidToken:
            return "Invalid decryption key", 400

        except Exception as e:
            return f"Error while processing: {str(e)}", 500

    else:
        return "Invalid method", 400

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
