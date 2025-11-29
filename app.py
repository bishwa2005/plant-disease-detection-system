import os
import json
import numpy as np
import tensorflow as tf
from PIL import Image
from io import BytesIO
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# --- App Setup ---
app = Flask(__name__)
CORS(app)
load_dotenv()

# --- Load Model, Info, and Class Names ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the script
MODEL_PATH = os.path.join(BASE_DIR, "trained_plant_disease_model.keras")
DISEASE_INFO_PATH = os.path.join(BASE_DIR, "disease_info.json")

try:
    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        print("✓ Model loaded successfully.")
    else:
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}.")
    
    if os.path.exists(DISEASE_INFO_PATH):
        with open(DISEASE_INFO_PATH, "r") as f:
            disease_info_db = json.load(f)
        print("✓ Disease info loaded successfully.")
    else:
        raise FileNotFoundError(f"Disease info file not found at {DISEASE_INFO_PATH}.")
except Exception as e:
    print(f"CRITICAL ERROR: Could not load model or disease_info.json. Error: {e}")
    exit()

# --- THIS IS THE FIX ---
# We convert the dict_keys object into a standard list.
CLASS_NAMES = list(disease_info_db.keys())
# ----------------------


def model_prediction(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image = image.resize((128, 128))
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])
    predictions = model.predict(input_arr)
    result_index = np.argmax(predictions)
    
    if result_index >= len(CLASS_NAMES):
        return "Unknown_Class"
    
    # This line will now work correctly
    return CLASS_NAMES[result_index]

# --- API Endpoints ---

@app.route("/")
def home():
    return "Plant Disease API Backend is running."

@app.route("/predict", methods=["POST"])
def predict():
    image_bytes = None
    try:
        if request.is_json:
            data = request.get_json()
            if "url" in data:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(data["url"], headers=headers)
                response.raise_for_status() 
                image_bytes = response.content
            else:
                return jsonify({"error": "No 'url' key provided in JSON payload"}), 400
        
        elif "file" in request.files:
            file = request.files["file"]
            image_bytes = file.read()
        
        else:
            return jsonify({"error": "No image file or URL provided"}), 400

        prediction_name = model_prediction(image_bytes)
        
        info = disease_info_db.get(prediction_name, {})
        symptoms = info.get("symptoms", "Info not found in database.")
        treatment = info.get("treatment", "Info not found in database.")
        prevention = info.get("prevention", "Info not found in database.")

        if "healthy" in prediction_name:
            symptoms = "No symptoms of disease detected. The plant appears healthy."
            treatment = "No treatment is necessary."
        
        return jsonify({
            "prediction": prediction_name,
            "disease_name": prediction_name.split('___')[-1].replace('_', ' ').replace('(including sour)', ''),
            "symptoms": symptoms,
            "treatment": treatment,
            "prevention": prevention
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to download image from URL. Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred during prediction: {str(e)}"}), 500

# (Your chat endpoint is unchanged)
chat_sessions = {}
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")
    session_id = data.get("session_id", "default_session")
    disease_context = data.get("disease", "a plant disease")
    symptoms_context = data.get("symptoms", "N/A")
    treatment_context = data.get("treatment", "N/A")
    prevention_context = data.get("prevention", "N/A")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    if session_id not in chat_sessions:
        memory = ConversationBufferMemory()
        
        template = f"""
        You are a helpful and empathetic botanist. You are assisting a user who has just identified: {disease_context}.
        Known symptoms are: {symptoms_context}
        Suggested general treatment is: {treatment_context}
        Suggested prevention tips are: {prevention_context}

        Your role is to have a natural, conversational dialogue. Be like a real human expert.
        Do not just repeat the information. Ask follow-up questions.

        Current conversation:
        {{history}}
        Human: {{input}}
        AI:
        """
        
        PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
            chat_sessions[session_id] = ConversationChain(
                llm=llm, prompt=PROMPT, memory=memory, verbose=False
            )
        except Exception as e:
            return jsonify({"error": f"Error initializing AI model. Is your GOOGLE_API_KEY correct? Error: {str(e)}"}), 500
    try:
        chain = chat_sessions[session_id]
        response = chain.run(user_message)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": f"An error occurred with the chatbot: {str(e)}"}), 500

# --- Run the Server ---
if __name__ == "__main__":
    print("Starting Plant Disease API Backend on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)