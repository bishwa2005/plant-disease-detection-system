import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image

# Function to load the trained model and make a prediction
def model_prediction(test_image):
    model = tf.keras.models.load_model("trained_plant_disease_model.keras")
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=(128, 128))
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])  # Convert single image to a batch
    predictions = model.predict(input_arr)
    return np.argmax(predictions)  # Return index of the class with the highest probability

# Sidebar
st.sidebar.title("Plant Disease Detection System")
app_mode = st.sidebar.selectbox("Select Page", ["🏠 HOME", "🔍 DISEASE RECOGNITION", "ℹ️ ABOUT"])

# Main Pages
if app_mode == "🏠 HOME":
    st.markdown("<h1 style='text-align: center;'>Plant Disease Detection System for Sustainable Agriculture</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to the **Plant Disease Detection System**! 🌱
    This application helps farmers and agricultural enthusiasts identify plant diseases from images. 
    Our system uses a powerful deep learning model to accurately recognize diseases in various crops,
    helping you take timely action to protect your plants and improve crop yield.
    """)
    
    try:
        img = Image.open("Diseases.png")
        st.image(img, caption="Our system can detect diseases in various plants.")
    except FileNotFoundError:
        st.warning("Could not find 'Diseases.png'. Please ensure the image is in the project directory.")
    
    st.info("""
    ### How It Works
    1. **Navigate** to the **'DISEASE RECOGNITION'** page using the sidebar.
    2. **Upload** an image of a plant leaf.
    3. **Get Instant Results**: Our model will analyze the image and tell you if the plant is healthy or has a disease.
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Why is this important?
    Early detection of plant diseases is crucial for sustainable agriculture. By using this tool, you can:
    * **Reduce crop loss** and increase productivity.
    * **Minimize the use of harmful pesticides**, promoting a healthier environment.
    * **Save time and resources** that would otherwise be spent on guesswork.
    """)

elif app_mode == "🔍 DISEASE RECOGNITION":
    st.header("🔍 Detect Plant Disease")
    st.markdown("Upload an image of a plant leaf, and our system will tell you its health status.")
    
    # Image upload
    test_image = st.file_uploader("Choose an Image:", type=["jpg", "jpeg", "png"])
    
    if test_image is not None:
        # Display the uploaded image
        st.image(test_image, caption="Uploaded Image")
        
        # Create a button for prediction
        if st.button("Predict"):
            st.write("---")
            with st.spinner("Analyzing image..."):
                try:
                    # Reading Labels
                    class_name = ['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
                                'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 
                                'Cherry_(including_sour)___healthy', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 
                                'Corn_(maize)___Common_rust_', 'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 
                                'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 
                                'Grape___healthy', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot',
                                'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 
                                'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy', 
                                'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew', 
                                'Strawberry___Leaf_scorch', 'Strawberry___healthy', 'Tomato___Bacterial_spot', 
                                'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 
                                'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 
                                'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus',
                                'Tomato___healthy']
                    
                    result_index = model_prediction(test_image)
                    
                    st.success("Analysis Complete!")
                    
                    # Displaying the result in a more user-friendly way
                    prediction = class_name[result_index]
                    if 'healthy' in prediction.lower():
                        st.balloons()
                        st.markdown(f"**Prediction:** This plant is likely **{prediction.split('___')[1].replace('_', ' ').replace('(including sour)', '').strip()}**! 🌱", unsafe_allow_html=True)
                    else:
                        st.warning(f"**Prediction:** This plant is likely suffering from **{prediction.split('___')[1].replace('_', ' ').replace('(including sour)', '').strip()}**.")
                        st.markdown("### Disease Information")
                        # You can add a more detailed description based on the predicted disease here
                        st.markdown(f"**Symptoms:** _Symptoms of this disease include..._")
                        st.markdown(f"**Suggested Treatment:** _To treat this disease, you can try..._")
                        
                except Exception as e:
                    st.error(f"An error occurred during prediction: {e}")
                    st.error("Please check if 'trained_plant_disease_model.keras' is in the project directory.")

elif app_mode == "ℹ️ ABOUT":
    st.header("About This Project")
    st.markdown("""
    This project was developed to provide an accessible and efficient tool for plant disease detection using deep learning. 
    It leverages a convolutional neural network (CNN) trained on a large dataset of plant leaves.
    
    **Our Goal:** To support sustainable agriculture by empowering farmers with a tool for early disease detection, reducing crop loss, and minimizing environmental impact.
    
    **Developed by:** [Your Name/Team Name]
    
    **Technology Stack:**
    - **Frontend:** Streamlit
    - **Backend:** TensorFlow, Keras
    - **Libraries:** NumPy, PIL
    """)
    st.markdown("---")
    st.header("Contact Us")
    st.markdown("""
    If you have any questions or feedback, please feel free to reach out.
    * **Email:** your.email@example.com
    * **GitHub:** [Link to your GitHub repository]
    """)