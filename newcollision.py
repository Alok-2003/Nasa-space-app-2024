import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from PIL import Image

# Load Data
@st.cache
def load_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    else:
        return None

# Preprocessing
def preprocess_data(data):
    data = data.dropna()  # Drop missing values

    # Handling 'Diameter' to convert it to numerical values
    data['Diameter'] = data['Diameter'].str.extract('(\d+\.?\d*)')[0].astype(float)

    # Convert a column to binary (0 or 1) based on a condition
    data['is_hazardous'] = data['rarity'].apply(lambda x: 1 if 'hazardous' in x.lower() else 0)

    return data

# Train the Model
def train_model(data):
    X = data[['Diameter', 'V relative(km/s)', 'CA DistanceMinimum (au)']]  # Feature selection
    y = data['is_hazardous']  # Target variable

    # Ensure there are samples from both classes
    if y.nunique() < 2:
        st.error("Not enough classes in the target variable for training.")
        return None, None, None

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression()
    model.fit(X_train, y_train)

    return model, X_test, y_test

# Function to process the uploaded image and detect if it's an asteroid
def classify_asteroid(image):
    # Convert the image to grayscale and calculate the mean pixel value
    image_gray = image.convert("L")
    image_array = np.array(image_gray)
    
    # Mock classification: Let's say we classify it as hazardous if the mean pixel value is less than a threshold
    mean_value = np.mean(image_array)
    if mean_value < 128:  # Example threshold for classification
        return True  # Hazardous object
    else:
        return False  # Non-hazardous object

# Function to plot a prediction graph
def plot_prediction_graph(is_hazardous):
    # Create data for the plot
    labels = ['Hazardous', 'Non-Hazardous']
    sizes = [1, 1]  # Initialize to 1 to display the predicted category
    if is_hazardous:
        sizes[0] += 1  # Increase hazardous count
    else:
        sizes[1] += 1  # Increase non-hazardous count

    # Create a pie chart
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig)

# App Layout
st.title("NEO Collision Prediction")

# Image upload
uploaded_image = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])
uploaded_file = st.file_uploader("Upload NEO Data CSV", type=["csv"])

if uploaded_file:
    data = load_data(uploaded_file)

    st.write("Data Overview:")
    st.write(data.head())

    if st.button("Train Model"):
        preprocessed_data = preprocess_data(data)
        model, X_test, y_test = train_model(preprocessed_data)

        if model:
            st.success("Model trained successfully!")

            # Model Evaluation
            predictions = model.predict(X_test)
            st.write("Confusion Matrix:")
            st.write(confusion_matrix(y_test, predictions))

            st.write("Classification Report:")
            st.text(classification_report(y_test, predictions))

            # Predicting New Data
            st.subheader("Predict Collision Probability")
            diameter = st.number_input("Diameter (m)", value=0.0)
            velocity = st.number_input("Velocity (km/s)", value=0.0)
            miss_distance = st.number_input("Miss Distance (au)", value=0.0)

            if st.button("Predict"):
                input_data = np.array([[diameter, velocity, miss_distance]])
                prediction = model.predict(input_data)
                st.write("Potential Collision: " + ("Yes" if prediction[0] == 1 else "No"))

if uploaded_image is not None:
    # Process the uploaded image here
    image = Image.open(uploaded_image)
    st.image(image, caption='Uploaded Image', use_column_width=True)

    # Classify the image to detect if it is an asteroid
    is_hazardous = classify_asteroid(image)
    prediction_text = "This image is classified as a hazardous object." if is_hazardous else "This image is classified as a non-hazardous object."
    st.write(prediction_text)

    # Plot prediction graph
    plot_prediction_graph(is_hazardous)
