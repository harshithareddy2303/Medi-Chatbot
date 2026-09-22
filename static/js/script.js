// ==========================================
// GET HTML ELEMENTS
// ==========================================

const messageInput =
    document.getElementById("messageInput");

const sendButton =
    document.getElementById("sendButton");

const chatBox =
    document.getElementById("chatBox");

const clearButton =
    document.getElementById("clearButton");

const historyButton =
    document.getElementById("historyButton");

const historyPanel =
    document.getElementById("historyPanel");

const historyContent =
    document.getElementById("historyContent");

const searchInput =
    document.getElementById("searchInput");

const searchButton =
    document.getElementById("searchButton");

const searchResults =
    document.getElementById("searchResults");


// ==========================================
// ADD MESSAGE
// ==========================================

function addMessage(message, sender, allowHTML = false) {

    const messageDiv =
        document.createElement("div");

    messageDiv.classList.add(
        "message",
        sender
    );


    const name =
        document.createElement("strong");


    if (sender === "user") {

        name.textContent = "You";

    } else {

        name.textContent = "MediChatbot";

    }


    messageDiv.appendChild(name);


    const paragraph =
        document.createElement("p");


    if (allowHTML) {

        paragraph.innerHTML = message;

    } else {

        paragraph.textContent = message;

    }


    messageDiv.appendChild(paragraph);

    chatBox.appendChild(messageDiv);


    chatBox.scrollTop =
        chatBox.scrollHeight;


    return messageDiv;
}


// ==========================================
// SEND MESSAGE
// ==========================================

async function sendMessage() {

    const message =
        messageInput.value.trim();


    if (message === "") {

        return;

    }


    // Add user message
    addMessage(
        message,
        "user"
    );


    // Clear input
    messageInput.value = "";


    // Disable button
    sendButton.disabled = true;


    // Show typing
    const typingMessage =
        addMessage(
            "Typing...",
            "bot"
        );


    try {

        const response =
            await fetch(
                "/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message
                    })
                }
            );


        if (!response.ok) {

            throw new Error(
                "Server error"
            );

        }


        const data =
            await response.json();


        // Remove typing
        typingMessage.remove();


        // Add bot response
        addMessage(
            data.response,
            "bot",
            true
        );


    } catch (error) {

        console.error(
            "Chat error:",
            error
        );


        typingMessage.remove();


        addMessage(
            "Sorry, something went wrong. Please make sure the Flask server is running and try again.",
            "bot"
        );


    } finally {

        sendButton.disabled = false;

        messageInput.focus();

        chatBox.scrollTop =
            chatBox.scrollHeight;

    }
}


// ==========================================
// SEND BUTTON
// ==========================================

sendButton.addEventListener(
    "click",
    sendMessage
);


// ==========================================
// ENTER KEY
// ==========================================

messageInput.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();

        }

    }
);


// ==========================================
// QUICK TOPIC BUTTONS
// ==========================================

const topicButtons =
    document.querySelectorAll(
        ".topic-button"
    );


topicButtons.forEach(
    function(button) {

        button.addEventListener(
            "click",
            function() {

                const topic =
                    button.getAttribute(
                        "data-topic"
                    );


                // Safety check
                if (!topic) {

                    console.error(
                        "Topic not found for button"
                    );

                    return;

                }


                messageInput.value =
                    "Tell me about " +
                    topic;


                sendMessage();

            }
        );

    }
);


// ==========================================
// CLEAR CHAT HISTORY
// ==========================================

clearButton.addEventListener(
    "click",
    async function() {

        const confirmClear =
            confirm(
                "Are you sure you want to clear the chat history?"
            );


        if (!confirmClear) {

            return;

        }


        try {

            const response =
                await fetch(
                    "/clear-history",
                    {
                        method: "DELETE"
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Unable to clear history"
                );

            }


            const data =
                await response.json();


            if (data.success) {

                chatBox.innerHTML = `

                    <div class="message bot">

                        <strong>MediChatbot</strong>

                        <p>
                            Hello! 👋 I can provide general
                            information about common health
                            conditions, symptoms, prevention
                            and self-care.
                        </p>

                        <p>
                            You can select a topic above or
                            type your health-related question
                            below.
                        </p>

                    </div>

                `;


                historyContent.innerHTML =
                    "<p>No chat history available.</p>";


                historyPanel.style.display =
                    "none";

            }

        } catch (error) {

            console.error(
                "Clear history error:",
                error
            );


            alert(
                "Unable to clear chat history. Please try again."
            );

        }

    }
);


// ==========================================
// SHOW / HIDE CHAT HISTORY
// ==========================================

historyButton.addEventListener(
    "click",
    async function() {

        if (
            historyPanel.style.display ===
            "block"
        ) {

            historyPanel.style.display =
                "none";

            return;

        }


        historyPanel.style.display =
            "block";


        historyContent.innerHTML =
            "<p>Loading history...</p>";


        try {

            const response =
                await fetch(
                    "/history"
                );


            if (!response.ok) {

                throw new Error(
                    "Unable to load history"
                );

            }


            const history =
                await response.json();


            if (history.length === 0) {

                historyContent.innerHTML =
                    "<p>No chat history available.</p>";

                return;

            }


            historyContent.innerHTML =
                "";


            history.forEach(
                function(item) {

                    const historyItem =
                        document.createElement(
                            "div"
                        );


                    historyItem.classList.add(
                        "history-item"
                    );


                    // User
                    const userTitle =
                        document.createElement(
                            "strong"
                        );

                    userTitle.textContent =
                        "You:";


                    const userMessage =
                        document.createElement(
                            "p"
                        );

                    userMessage.textContent =
                        item.user_message;


                    // Bot
                    const botTitle =
                        document.createElement(
                            "strong"
                        );

                    botTitle.textContent =
                        "MediChatbot:";


                    const botMessage =
                        document.createElement(
                            "p"
                        );


                    botMessage.innerHTML =
                        item.bot_response;


                    // Date
                    const date =
                        document.createElement(
                            "small"
                        );

                    date.textContent =
                        item.created_at;


                    historyItem.appendChild(
                        userTitle
                    );

                    historyItem.appendChild(
                        userMessage
                    );

                    historyItem.appendChild(
                        botTitle
                    );

                    historyItem.appendChild(
                        botMessage
                    );

                    historyItem.appendChild(
                        date
                    );


                    historyContent.appendChild(
                        historyItem
                    );

                }
            );


        } catch (error) {

            console.error(
                "History error:",
                error
            );


            historyContent.innerHTML =
                "<p>Unable to load chat history.</p>";

        }

    }
);


// ==========================================
// SEARCH MEDICAL TOPICS
// ==========================================

async function searchTopics() {

    const query =
        searchInput.value.trim();


    if (query === "") {

        searchResults.innerHTML =
            "<p>Please enter a health topic.</p>";

        return;

    }


    searchResults.innerHTML =
        "<p>Searching...</p>";


    try {

        const response =
            await fetch(
                "/api/search?q=" +
                encodeURIComponent(query)
            );


        if (!response.ok) {

            throw new Error(
                "Search failed"
            );

        }


        const data =
            await response.json();


        if (
            !data.results ||
            data.results.length === 0
        ) {

            searchResults.innerHTML =
                "<p>No matching health topic found.</p>";

            return;

        }


        searchResults.innerHTML =
            "";


        data.results.forEach(
            function(item) {

                const result =
                    document.createElement(
                        "div"
                    );


                result.classList.add(
                    "search-result"
                );


                const title =
                    document.createElement(
                        "h4"
                    );

                title.textContent =
                    item.name;


                const description =
                    document.createElement(
                        "p"
                    );

                description.textContent =
                    item.description;


                result.appendChild(
                    title
                );

                result.appendChild(
                    description
                );


                // Click search result
                result.addEventListener(
                    "click",
                    function() {

                        messageInput.value =
                            "Tell me about " +
                            item.name;


                        sendMessage();


                        searchResults.innerHTML =
                            "";


                        searchInput.value =
                            "";

                    }
                );


                searchResults.appendChild(
                    result
                );

            }
        );


    } catch (error) {

        console.error(
            "Search error:",
            error
        );


        searchResults.innerHTML =
            "<p>Unable to search topics. Please try again.</p>";

    }
}


// ==========================================
// SEARCH BUTTON
// ==========================================

searchButton.addEventListener(
    "click",
    searchTopics
);


// ==========================================
// SEARCH ENTER KEY
// ==========================================

searchInput.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            event.preventDefault();

            searchTopics();

        }

    }
);