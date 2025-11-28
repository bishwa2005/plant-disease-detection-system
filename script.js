// The URL of your Flask backend
const API_URL = "http://127.0.0.1:5000";

// --- Page Element References ---
const imageUploader = document.getElementById("image-uploader");
const urlUploader = document.getElementById("url-uploader");
const predictButton = document.getElementById("predict-button");
const imagePreview = document.getElementById("image-preview");

const preventionCard = document.getElementById("prevention-card");
const resultsDiv = document.getElementById("results");

const predictionOutput = document.getElementById("prediction-output");
const symptomsOutput = document.getElementById("symptoms-output");
const treatmentOutput = document.getElementById("treatment-output");
const preventionOutput = document.getElementById("prevention-output"); // <-- NEW
const symptomsSection = document.getElementById("symptoms-section");   // <-- NEW
const treatmentSection = document.getElementById("treatment-section"); // <-- NEW
const preventionTitle = document.getElementById("prevention-title");   // <-- NEW

const chatContainer = document.getElementById("chat-container");
const chatBox = document.getElementById("chat-box");
const chatInput = document.getElementById("chat-message");
const chatSendButton = document.getElementById("chat-send-button");
const uploadArea = document.getElementById("upload-area");
const uploadLabel = document.querySelector(".upload-label");

// --- Global state ---
let chatContext = {
    session_id: "user_" + Date.now(),
    disease: "",
    symptoms: "",
    treatment: "",
    prevention: "" // <-- NEW
};
let currentFile = null;

// --- Drag/Drop, File, and URL Logic (Unchanged) ---
uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('dragover'); });
uploadArea.addEventListener('dragleave', () => { uploadArea.classList.remove('dragover'); });
uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) handleFile(file);
});
imageUploader.addEventListener("change", () => {
    const file = imageUploader.files[0];
    if (file) handleFile(file);
});
function handleFile(file) {
    currentFile = file;
    urlUploader.value = ""; 
    const reader = new FileReader();
    reader.onload = (e) => { imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`; };
    reader.readAsDataURL(file);
    uploadLabel.textContent = file.name;
    imagePreview.style.display = "block";
}
urlUploader.addEventListener("input", () => {
    const url = urlUploader.value.trim();
    if (url) {
        currentFile = null;
        imageUploader.value = ""; 
        uploadLabel.textContent = "Click to upload or drag & drop";
        imagePreview.innerHTML = `<img src="${url}" alt="Image URL Preview" onerror="this.parentElement.style.display='none';">`;
        imagePreview.style.display = "block";
    } else {
        imagePreview.innerHTML = "";
        imagePreview.style.display = "none";
    }
});

// --- Prediction Logic ---
predictButton.addEventListener("click", async () => {
    const imageUrl = urlUploader.value.trim();
    let requestBody, requestHeaders = {};

    if (currentFile) {
        const formData = new FormData();
        formData.append("file", currentFile);
        requestBody = formData;
    } else if (imageUrl) {
        requestBody = JSON.stringify({ "url": imageUrl });
        requestHeaders["Content-Type"] = "application/json";
    } else {
        alert("Please choose an image file, drag one in, or paste an image URL.");
        return;
    }

    setLoading(true);
    preventionCard.classList.add("hidden"); // Hide general tips
    resultsDiv.classList.add("hidden");
    chatContainer.classList.add("hidden");

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: "POST",
            headers: requestHeaders,
            body: requestBody,
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || "Prediction failed");
        }
        const data = await response.json();
        
        displayPrediction(data); // This will show the results
        
        // --- MODIFIED: Save all 3 pieces of context for the chat ---
        chatContext.disease = data.disease_name;
        chatContext.symptoms = data.symptoms;
        chatContext.treatment = data.treatment;
        chatContext.prevention = data.prevention; // <-- NEW
        // ----------------------------------------------------

        chatBox.innerHTML = "";
        addMessageToChat(`Hello! I see your plant might have **${data.disease_name}**. You can ask me any follow-up questions about symptoms, treatment, or prevention.`, "bot");

    } catch (error) {
        alert("Error: " + error.message);
        if (imageUrl) imagePreview.innerHTML = "";
        preventionCard.classList.remove("hidden"); // Show general tips again on error
    } finally {
        setLoading(false);
    }
});

function setLoading(isLoading) {
    if (isLoading) {
        predictButton.disabled = true;
        predictButton.textContent = "Analyzing...";
    } else {
        predictButton.disabled = false;
        predictButton.textContent = "Analyze Image";
    }
}

function displayPrediction(data) {
    predictionOutput.textContent = data.disease_name;
    symptomsOutput.innerHTML = data.symptoms.replace(/\n/g, '<br>');
    treatmentOutput.innerHTML = data.treatment.replace(/\n/g, '<br>');
    preventionOutput.innerHTML = data.prevention.replace(/\n/g, '<br>'); // <-- NEW

    if (data.prediction.includes("healthy")) {
        predictionOutput.classList.add("healthy");
        // Hide symptoms/treatment, rename prevention
        symptomsSection.classList.add("hidden");
        treatmentSection.classList.add("hidden");
        preventionTitle.textContent = "How to Keep it Healthy"; // <-- NEW
    } else {
        predictionOutput.classList.remove("healthy");
        // Show all sections
        symptomsSection.classList.remove("hidden");
        treatmentSection.classList.remove("hidden");
        preventionTitle.textContent = "Prevention"; // <-- NEW
    }
    
    resultsDiv.classList.remove("hidden"); // Show the results card
    chatContainer.classList.remove("hidden");
}

// --- Chat Logic ---
chatSendButton.addEventListener("click", sendChatMessage);
chatInput.addEventListener("keyup", (e) => {
    if (e.key === "Enter") sendChatMessage();
});

async function sendChatMessage() {
    const message = chatInput.value.trim();
    if (message === "") return;

    addMessageToChat(message, "user");
    chatInput.value = "";
    chatSendButton.disabled = true;

    const typingIndicator = document.createElement("div");
    typingIndicator.classList.add("chat-msg", "bot", "typing");
    typingIndicator.textContent = "Expert is thinking...";
    chatBox.appendChild(typingIndicator);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            // --- MODIFIED: Send all context to the bot ---
            body: JSON.stringify({
                message: message,
                session_id: chatContext.session_id,
                disease: chatContext.disease,
                symptoms: chatContext.symptoms,
                treatment: chatContext.treatment,
                prevention: chatContext.prevention // <-- NEW
            }),
        });
        
        chatBox.removeChild(typingIndicator);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || "Chat failed");
        }
        const data = await response.json();
        addMessageToChat(data.response, "bot");

    } catch (error) {
        if (chatBox.contains(typingIndicator)) chatBox.removeChild(typingIndicator);
        addMessageToChat("Sorry, I ran into an error: " + error.message, "bot");
    } finally {
        chatSendButton.disabled = false;
        chatInput.focus();
    }
}
function addMessageToChat(text, sender) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("chat-msg", sender);
    msgDiv.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}