function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    let chatBox = document.getElementById("chat-box");

    if (userInput.trim() === "") return;

    // Append user message to chat
    chatBox.innerHTML += `<div class='message user'><strong>You:</strong> ${userInput}</div>`;
    document.getElementById("user-input").value = "";

    // Send request to Flask backend at the correct URL
    fetch("http://127.0.0.1:5000/query", {  // Ensure this is your Flask server URL
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userInput })
    })
    .then(response => response.json())  // Parse JSON response
    .then(data => {
        let botResponse = data.response || "Sorry, I couldn't understand that.";
        chatBox.innerHTML += `<div class='message bot'><strong>Bot:</strong> ${formatResponse(botResponse)}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        console.error("Error:", error);
        chatBox.innerHTML += `<div class='message bot error'><strong>Bot:</strong> Error processing request.</div>`;
    });
}

function formatResponse(response) {
    return response.replace(/\*\*(.*?)\*\*/g, '<h3 class="title">$1</h3>')  // Styled section titles
                   .replace(/\*(.*?)\*/g, '<strong class="highlight">$1</strong>')  // Styled key points
                   .replace(/\+ (.*?)\n/g, '<li class="list-item">$1</li><br>')  // Styled list items
                   .replace(/\n/g, '<br>');  // Preserve line breaks
}