chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log("Background.js received message:", message); // ✅ Debugging log

    if (message.text) {
        chrome.notifications.create({
            type: "basic",
            iconUrl: chrome.runtime.getURL("icon.png"), // Ensure this file exists
            title: "Extracted PDF Text",
            message: message.text || "No content extracted."
        }, () => {
            if (chrome.runtime.lastError) {
                console.error("Notification error:", chrome.runtime.lastError.message);
            }
        });

        sendResponse({ success: true });
    } else {
        console.warn("No text received in background.js");
        sendResponse({ success: false });
    }

    return true; // Keeps service worker active
});
