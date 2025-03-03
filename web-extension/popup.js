import * as pdfjsLib from "./libs/pdf.mjs";

document.getElementById("pdfInput").addEventListener("change", async (event) => {
    if (!pdfjsLib) {
        console.error("PDF.js library failed to load.");
        return;
    }

    pdfjsLib.GlobalWorkerOptions.workerSrc = chrome.runtime.getURL("libs/pdf.worker.mjs");
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = async function () {
            try {
                const typedArray = new Uint8Array(reader.result);
                const pdf = await pdfjsLib.getDocument({ data: typedArray }).promise;
                let text = "";

                for (let i = 1; i <= pdf.numPages; i++) {
                    const page = await pdf.getPage(i);
                    const content = await page.getTextContent();
                    text += content.items.map(item => item.str).join(" ") + "\n";
                }
                
                console.log("Extracted Text from PDF:", text);
                
                // Split tweets based on special marker '###'
                let tweets = text.split("###").map(t => t.trim()).filter(t => t.length > 0);
                
                // Send all tweets in a single request
                if (tweets.length > 0) {
                    fetch("http://127.0.0.1:5000/predict", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ tweet: tweets.join("###") })
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log("API Response:", data);

                        if (data.predictions && data.predictions.length === tweets.length) {
                            for (let i = 0; i < tweets.length; i++) {
                                chrome.runtime.sendMessage({ tweet: tweets[i], prediction: data.predictions[i] });
                            }
                        } else {
                            console.error("Mismatch in tweet count and predictions:", data);
                        }
                    })
                    .catch(error => console.error("Error communicating with API:", error));
                }
            } catch (error) {
                console.error("PDF processing error:", error);
            }
        };
        reader.readAsArrayBuffer(file);
    }
});