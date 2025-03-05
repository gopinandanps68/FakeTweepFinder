document.getElementById("csvInput").addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) {
        console.error("No file selected.");
        return;
    }

    const reader = new FileReader();
    reader.onload = async (e) => {
        const csvText = e.target.result;
        const rows = csvText.split("\n").map(row => row.trim()).filter(row => row.length > 0);

        if (rows.length === 0) {
            console.warn("No valid data found in CSV.");
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5000/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ tweet: rows })
            });

            if (!response.ok) {
                throw new Error(`Prediction API Failed: ${response.statusText}`);
            }

            const predictions = await response.json();
            console.log("API Predictions:", predictions);

            if (predictions.predictions && predictions.predictions.length === rows.length) {
                for (let i = 0; i < rows.length; i++) {
                    chrome.runtime.sendMessage({ 
                        tweet: rows[i], 
                        prediction: predictions.predictions[i] 
                    }, response => {
                        if (chrome.runtime.lastError) {
                            console.error("Error sending message to background:", chrome.runtime.lastError);
                        }
                    });
                }
            } else {
                console.error("Mismatch in tweet count and predictions:", predictions);
            }
        } catch (error) {
            console.error("Error communicating with Prediction API:", error);
        }
    };

    reader.readAsText(file);
});
