from flask import Flask, request, jsonify
import joblib
import numpy as np
import re
import nltk
import traceback
import pandas as pd
import os
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import fasttext
import fasttext.util

# Download NLTK resources
nltk.download('stopwords')

app = Flask(__name__)

# Ensure NLTK path is correctly set
nltk.data.path.append(os.path.expanduser("~/nltk_data"))

# Load models
try:
    vectorizer_en = joblib.load('tfidf_vectorizer.pkl')
    model_en = joblib.load('logistic_regression_model.pkl')
    model_ml = joblib.load('bot_detection_rf_model_malayalam.pkl')
except Exception as e:
    print(f"Error loading model: {e}")
    traceback.print_exc()

# Load FastText model for Malayalam
try:
    fasttext.util.download_model('ml', if_exists='ignore')
    ft_model = fasttext.load_model('cc.ml.300.bin')
except Exception as e:
    print(f"Error loading FastText model: {e}")
    traceback.print_exc()
    ft_model = None  # Set to None to avoid crashes

# Detect language
def detect_language(text):
    if re.search("[\u0D00-\u0D7F]", text):
        return "ml"
    return "en"

# Preprocess English text
def preprocess_text_en(text):
    try:
        pstem = PorterStemmer()
        text = re.sub("[^a-zA-Z]", " ", text).lower().split()
        
        try:
            stop_words = set(stopwords.words('english'))  # Load stopwords safely
        except Exception as e:
            print("Error loading stopwords:", e)
            stop_words = set()  # Fallback to an empty set

        text = [pstem.stem(word) for word in text if word not in stop_words]
        return " ".join(text)
    except Exception as e:
        print(f"Error processing English text: {e}")
        traceback.print_exc()
        return ""

# Preprocess Malayalam text
def preprocess_text_ml(text):
    try:
        text = re.sub("[^\u0D00-\u0D7F]", " ", text)  # Remove non-Malayalam characters
        words = text.split()
        if ft_model:  # Ensure model is loaded
            word_vectors = [ft_model.get_word_vector(word) for word in words if word in ft_model]
            if not word_vectors:
                return np.zeros((1, 300))
            return np.mean(word_vectors, axis=0).reshape(1, -1)
        else:
            return np.zeros((1, 300))  # Default if FastText failed
    except Exception as e:
        print(f"Error processing Malayalam text: {e}")
        traceback.print_exc()
        return np.zeros((1, 300))

# Prediction API
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data or 'tweet' not in data:
            return jsonify({"error": "Invalid input, 'tweet' key missing"}), 400
        
        tweets = data['tweet']
        predictions = []

        for tweet in tweets:
            lang = detect_language(tweet)
            if lang == "en":
                processed_text = preprocess_text_en(tweet)
                vectorized_text = vectorizer_en.transform([processed_text]).toarray()
                prediction = model_en.predict(vectorized_text)
            else:
                vectorized_text = preprocess_text_ml(tweet)
                prediction = model_ml.predict(vectorized_text)

            predictions.append("HUMAN" if prediction[0] == 1 else "BOT")

        return jsonify({"predictions": predictions})

    except Exception as e:
        print(f"Error in prediction: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500  # Always return JSON

# New API to handle CSV upload
@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    csv_file = request.files["file"]
    if csv_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        df = pd.read_csv(csv_file)
        if 'tweet' not in df.columns:
            return jsonify({"error": "CSV must contain a 'tweet' column"}), 400
        tweets = df['tweet'].dropna().tolist()
        return jsonify({"tweets": tweets})
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
