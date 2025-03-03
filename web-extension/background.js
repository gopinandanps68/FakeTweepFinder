chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log("Received message:", message);

    if (message.prediction && message.tweet) {
        let fullTweet = message.tweet;
        let shortTweet = fullTweet.length > 200 ? fullTweet.substring(0, 200) + "..." : fullTweet;

        chrome.notifications.create({
            type: "basic",
            iconUrl: chrome.runtime.getURL("icon.png"),
            title: "Tweet Classification",
            message: `Tweet: ${shortTweet}\n\nPrediction: ${message.prediction}`
        }, (notificationId) => {
            if (chrome.runtime.lastError) {
                console.error("Notification error:", chrome.runtime.lastError.message);
            } else {
                console.log("Notification created successfully:", notificationId);
                // Store full tweet in storage for later access
                chrome.storage.local.set({ [notificationId]: fullTweet });
            }
        });

        sendResponse({ success: true });
    } else {
        console.warn("Invalid message received:", message);
    }
});
