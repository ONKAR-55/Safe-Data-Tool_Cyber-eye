from flask import Flask, render_template, request, send_from_directory
import os
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    file = request.files['file']
    method = request.form['method']

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    df = pd.read_csv(filepath)

    if method == 'mask':
        df['Name'] = df['Name'].apply(lambda x: 'XXX')
    elif method == 'encrypt':
        df['Name'] = df['Name'].apply(lambda x: ''.join(reversed(str(x))))
    elif method == 'anonymize':
        df['Name'] = 'Anonymous'

    processed_file = os.path.join(PROCESSED_FOLDER, 'processed_' + file.filename)
    df.to_csv(processed_file, index=False)

    # Visualization
    plt.figure()
    df['Age'].value_counts().plot(kind='bar')
    plt.title('Age Distribution')
    plt.xlabel('Age')
    plt.ylabel('Count')
    plot_path = os.path.join('static', 'plot.png')
    plt.savefig(plot_path)
    plt.close()

    return render_template('result.html', plot_url=plot_path, filename='processed_' + file.filename)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(PROCESSED_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)