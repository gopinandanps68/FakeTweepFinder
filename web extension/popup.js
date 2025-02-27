import * as pdfjsLib from "./libs/pdf.mjs"; // Import all named exports

document.getElementById("pdfInput").addEventListener("change", async (event) => {
    if (!pdfjsLib) {
        console.error("PDF.js library failed to load.");
        return;
    }

    // Set worker source to the locally stored file inside 'libs/'
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

                // Output the extracted text in the console (for debugging)
                console.log("Extracted Text from PDF:\n", text);

                // ✅ Send the extracted text to background.js for notification
                chrome.runtime.sendMessage({ text: text.substring(0, 100) }, (response) => {
                    if (chrome.runtime.lastError) {
                        console.error("Error sending message:", chrome.runtime.lastError.message);
                    } else if (response) {
                        console.log("Message successfully sent to background.js:", response);
                    } else {
                        console.warn("No response received from background.js");
                    }
                });

            } catch (error) {
                console.error("PDF processing error:", error);
            }
        };
        reader.readAsArrayBuffer(file);
    }
});
