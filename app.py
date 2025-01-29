from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

nltk.download('stopwords')

app = Flask(__name__)

# Load the trained model and vectorizer
vectorizer = joblib.load('tfidf_vectorizer.pkl')
model = joblib.load('logistic_regression_model.pkl')

def preprocess_text(text):
    pstem = PorterStemmer()
    text = re.sub("[^a-zA-Z]", " ", text)
    text = text.lower()
    text = text.split()
    text = [pstem.stem(word) for word in text if word not in set(stopwords.words('english'))]
    return " ".join(text)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    text = request.form['tweet']
    processed_text = preprocess_text(text)
    vectorized_text = vectorizer.transform([processed_text]).toarray()
    prediction = model.predict(vectorized_text)
    result = "HUMAN" if prediction[0] == 0 else "BOT"
    return render_template('index.html', prediction_text=f'Tweet is {result}')

if __name__ == "__main__":
    app.run(debug=True)
