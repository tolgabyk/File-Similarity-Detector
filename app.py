from flask import Flask, request, render_template
import pdfplumber
import numpy as np
from docx import Document

app = Flask(__name__)

def minimum(a, b, c):
    if a <= b and a <= c:
        return a
    if b <= c and b <= a:
        return b
    return c

def normalize(X, size):
    if len(X) < size:
        fark = size - len(X)
        X = X + " " * fark
    return X

def levenshtein_mesafesi(A, B):
    K = np.zeros((len(A) + 1, len(B) + 1))
    A_len = len(A)
    B_len = len(B)

    for i in range(A_len + 1):
        K[i][0] = i
    for j in range(B_len + 1):
        K[0][j] = j

    for i in range(1, A_len + 1):
        for j in range(1, B_len + 1):
            if A[i - 1] == B[j - 1]:
                K[i][j] = K[i - 1][j - 1]
            else:
                silme = K[i - 1][j] + 1
                ekleme = K[i][j - 1] + 1
                yerdegistirme = K[i - 1][j - 1] + 1
                K[i][j] = minimum(silme, ekleme, yerdegistirme)

    return K[A_len][B_len]

def pdf_to_text(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"PDF dosyası işlenirken hata oluştu: {e}")
        return ""

def docx_to_text(file):
    try:
        doc = Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        print(f"DOCX dosyası işlenirken hata oluştu: {e}")
        return ""

def txt_to_text(file):
    try:
        return file.read().decode('utf-8')
    except Exception as e:
        print(f"TXT dosyası işlenirken hata oluştu: {e}")
        return ""

def extract_text(file):
    if file.filename.endswith('.pdf'):
        return pdf_to_text(file)
    elif file.filename.endswith('.docx'):
        return docx_to_text(file)
    elif file.filename.endswith('.txt'):
        return txt_to_text(file)
    else:
        raise ValueError("Desteklenmeyen dosya türü")

@app.route('/', methods=['GET', 'POST'])
def index():
    similarity = None  
    error = None  

    if request.method == 'POST':
        file1 = request.files['file1']
        file2 = request.files['file2']

        try:
            text1 = extract_text(file1)
            text2 = extract_text(file2)
            if not text1 or not text2:
                raise ValueError("Dosyalar boş veya işlenemiyor.")
        except ValueError as e:
            error = str(e)
            return render_template('index.html', error=error, similarity=similarity)

        max_len = max(len(text1), len(text2))
        text1 = normalize(text1, max_len)
        text2 = normalize(text2, max_len)

        mesafe = levenshtein_mesafesi(text1, text2)
        similarity = (max_len - mesafe) / max_len

    return render_template('index.html', similarity=similarity, error=error)

if __name__ == '__main__':
    app.run(debug=True)
