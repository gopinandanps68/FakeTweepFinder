from flask import Flask, request, jsonify
import joblib
import numpy as np
import re
import nltk
import traceback
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import fasttext
import fasttext.util

nltk.download('stopwords')
nltk.data.path.append("C:/Users/KALARICKAL/nltk_data")  # Ensure correct NLTK path

app = Flask(__name__)

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

def detect_language(text):
    if re.search("[\u0D00-\u0D7F]", text):
        return "ml"
    return "en"

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

def preprocess_text_ml(text):
    try:
        text = re.sub("[^\u0D00-\u0D7F]", " ", text)
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

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data or 'tweet' not in data:
            return jsonify({"error": "Invalid input, 'tweet' key missing"}), 400
        
        tweets = [t.strip() for t in data['tweet'].split("###") if t.strip()]
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

        return jsonify({"predictions": predictions})  # Ensure it's always a list

    except Exception as e:
        print(f"Error in prediction: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500  # Always return JSON

if __name__ == "__main__":
    app.run(debug=True)