chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log("Received message:", message);

    if (message.prediction && message.tweet) {
        let fullTweet = message.tweet;
        let prediction = message.prediction;

        chrome.notifications.create({
            type: "basic",
            iconUrl: chrome.runtime.getURL("icon.png"),
            title: "Tweet Classification",
            message: `Prediction: ${prediction}\n\nTweet: ${fullTweet}`
        }, (notificationId) => {
            if (chrome.runtime.lastError) {
                console.error("Notification error:", chrome.runtime.lastError.message);
            } else {
                console.log("Notification created successfully:", notificationId);
            }
        });

        sendResponse({ success: true });
    } else {
        console.warn("Invalid message received:", message);
    }
});
