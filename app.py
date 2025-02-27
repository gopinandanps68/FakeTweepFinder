from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import fasttext
import fasttext.util

nltk.download('stopwords')

app = Flask(__name__)

# Load the English model and vectorizer
vectorizer_en = joblib.load('tfidf_vectorizer.pkl')
model_en = joblib.load('logistic_regression_model.pkl')

# Load the Malayalam model
model_ml = joblib.load('bot_detection_rf_model_malayalam.pkl')

# Load the fastText language model for Malayalam word embeddings
fasttext.util.download_model('ml', if_exists='ignore')  # Ensures the model is available
ft_model = fasttext.load_model('cc.ml.300.bin')

# Function to detect language (simple heuristic based on character patterns)
def detect_language(text):
    if re.search("[\u0D00-\u0D7F]", text):  # Malayalam Unicode range
        return "ml"
    return "en"

# Text preprocessing for English
def preprocess_text_en(text):
    pstem = PorterStemmer()
    text = re.sub("[^a-zA-Z]", " ", text)
    text = text.lower()
    text = text.split()
    text = [pstem.stem(word) for word in text if word not in set(stopwords.words('english'))]
    return " ".join(text)

# Text preprocessing for Malayalam using fastText embeddings
def preprocess_text_ml(text):
    text = re.sub("[^\u0D00-\u0D7F]", " ", text)  # Remove non-Malayalam characters
    words = text.split()
    vectorized_text = np.mean([ft_model.get_word_vector(word) for word in words if word in ft_model], axis=0)
    return vectorized_text.reshape(1, -1)  # Ensuring correct shape for model prediction

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    text = request.form['tweet']
    lang = detect_language(text)

    if lang == "en":
        processed_text = preprocess_text_en(text)
        vectorized_text = vectorizer_en.transform([processed_text]).toarray()
        prediction = model_en.predict(vectorized_text)
    else:
        vectorized_text = preprocess_text_ml(text)
        prediction = model_ml.predict(vectorized_text)

    result = "BOT" if prediction[0] == 0 else "HUMAN"
    return render_template('index.html', prediction_text=f'Tweet is {result} (Language: {lang.upper()})')

if __name__ == "__main__":
    app.run(debug=True)
