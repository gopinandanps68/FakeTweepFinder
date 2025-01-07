from flask import Flask, render_template, request, redirect, url_for
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import numpy as np
import joblib
import os

# Download necessary NLTK data
nltk.download('stopwords')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/api", methods=["GET", "POST"])
def api():
    if request.method == "POST":
        try:
            # Load model and words
            words_path = 'words.pkl'
            model_path = 'model.pkl'

            if not os.path.exists(words_path) or not os.path.exists(model_path):
                return render_template("index.html", error="Model or words file missing!")

            words = joblib.load(words_path)
            model = joblib.load(model_path)
            pstem = PorterStemmer()

            # Process input tweet
            tweet = request.form.get("tweet", "")
            text = re.sub("[^a-zA-Z]", ' ', tweet).lower().split()
            text = [pstem.stem(word) for word in text if word not in set(stopwords.words('english'))]
            text = ' '.join(text)

            # Create query vector
            query = [1 if word in text else 0 for word in words]

            # Make prediction
            prediction = model.predict(np.array([query]))[0]

            if prediction == 1:
                msg = "Human generated"
                return render_template("index.html", msg=msg, tweet=tweet)
            if prediction == 0:
                error = "Bot generated"
                return render_template("index.html", error=error, tweet=tweet)
            else:
                msg = "Human generated"
                return render_template("index.html", msg=msg, tweet=tweet)
        except Exception as e:
            return render_template("index.html", msg=f"An error occurred: {e}")
    else:
        # Redirect to index page for GET requests
        return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)
