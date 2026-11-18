import streamlit as st
import requests
import json
import time
import os

# Set the page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="House Price Predictor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add title and description
st.title("House Price Prediction")
st.markdown(
    """
    <p style="font-size: 18px; color: gray;">
        A simple MLOps demonstration project for real-time house price prediction
    </p>
    """,
    unsafe_allow_html=True,
)

# Create a two-column layout
col1, col2 = st.columns(2, gap="large")

# Input form
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Square Footage slider
    st.markdown(f"<p><strong>Square Footage:</strong> <span id='sqft-value'></span></p>", unsafe_allow_html=True)
    sqft = st.slider("", 500, 5000, 1500, 50, label_visibility="collapsed", key="sqft")
    st.markdown(f"<script>document.getElementById('sqft-value').innerText = '{sqft} sq ft';</script>", unsafe_allow_html=True)
    
    # Bedrooms and Bathrooms in two columns
    bed_col, bath_col = st.columns(2)
    with bed_col:
        st.markdown("<p><strong>Bedrooms</strong></p>", unsafe_allow_html=True)
        bedrooms = st.selectbox("", options=[1, 2, 3, 4, 5, 6], index=2, label_visibility="collapsed")
    
    with bath_col:
        st.markdown("<p><strong>Bathrooms</strong></p>", unsafe_allow_html=True)
        bathrooms = st.selectbox("", options=[1, 1.5, 2, 2.5, 3, 3.5, 4], index=2, label_visibility="collapsed")
    
    # Location dropdown
    st.markdown("<p><strong>Location</strong></p>", unsafe_allow_html=True)
    location = st.selectbox("", options=["Urban", "Suburban", "Rural", "Urban", "Waterfront", "Mountain"], index=1, label_visibility="collapsed")
    
    # Year Built slider
    st.markdown(f"<p><strong>Year Built:</strong> <span id='year-value'></span></p>", unsafe_allow_html=True)
    year_built = st.slider("", 1900, 2025, 2000, 1, label_visibility="collapsed", key="year")
    st.markdown(f"<script>document.getElementById('year-value').innerText = '{year_built}';</script>", unsafe_allow_html=True)
    
    # Predict button
    predict_button = st.button("Predict Price", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Results section
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h2>Prediction Results</h2>", unsafe_allow_html=True)
    
    # If button is clicked, show prediction
    if predict_button:
        # Show loading spinner
        with st.spinner("Calculating prediction..."):
            # Prepare data for API call
            api_data = {
                "sqft": sqft,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "location": location.lower(),
                "year_built": year_built,
                "condition": "Good"
            }
            
            try:
                # Get API endpoint from environment variable or use default
                api_endpoint = os.getenv("API_URL", "http://localhost:8000")
                predict_url = f"{api_endpoint.rstrip('/')}/predict"
                
                st.write(f"Connecting to API at: {predict_url}")
                
                # Make API call to FastAPI backend
                response = requests.post(predict_url, json=api_data)
                response.raise_for_status()  # Raise exception for bad status codes
                prediction = response.json()
                
                # Store prediction in session state
                st.session_state.prediction = prediction
                st.session_state.prediction_time = time.time()
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to API: {e}")
                st.warning("Using mock data for demonstration purposes. Please check your API connection.")
                # For demo purposes, use mock data if API fails
                st.session_state.prediction = {
                    "predicted_price": 467145,
                    "confidence_interval": [420430.5, 513859.5],
                    "features_importance": {
                        "sqft": 0.43,
                        "location": 0.27,
                        "bathrooms": 0.15
                    },
                    "prediction_time": "0.12 seconds"
                }
                st.session_state.prediction_time = time.time()
    
    # Display prediction if available
    if "prediction" in st.session_state:
        pred = st.session_state.prediction
        
        # Format the predicted price
        formatted_price = "${:,.0f}".format(pred["predicted_price"])
        st.markdown(f'<div class="prediction-value">{formatted_price}</div>', unsafe_allow_html=True)
        
        # Display confidence score and model used
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown('<p class="info-label">Confidence Score</p>', unsafe_allow_html=True)
            st.markdown('<p class="info-value">92%</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_b:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown('<p class="info-label">Model Used</p>', unsafe_allow_html=True)
            st.markdown('<p class="info-value">XGBoost</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display price range and prediction time
        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown('<p class="info-label">Price Range</p>', unsafe_allow_html=True)
            lower = "${:,.1f}".format(pred["confidence_interval"][0])
            upper = "${:,.1f}".format(pred["confidence_interval"][1])
            st.markdown(f'<p class="info-value">{lower} - {upper}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_d:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown('<p class="info-label">Prediction Time</p>', unsafe_allow_html=True)
            st.markdown('<p class="info-value">0.12 seconds</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Top factors
        st.markdown('<div class="top-factors">', unsafe_allow_html=True)
        st.markdown("<p><strong>Top Factors Affecting Price:</strong></p>", unsafe_allow_html=True)
        st.markdown("""
        <ul>
            <li>Square Footage</li>
            <li>Number of Bedrooms/Bathrooms</li>
        </ul>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Display placeholder message
        st.markdown("""
        <div style="display: flex; height: 300px; align-items: center; justify-content: center; color: #6b7280; text-align: center;">
            Fill out the form and click "Predict Price" to see the estimated house price.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Add footer
st.markdown("<hr>", unsafe_allow_html=True)  # Add a horizontal line for separation
st.markdown(
    """
    <div style="text-align: center; color: gray; margin-top: 20px;">
        <p><strong>Built for MLOps Bootcamp</strong></p>
        <p>by <a href="https://www.schoolofdevops.com" target="_blank">School of Devops</a></p>
    </div>
    """,
    unsafe_allow_html=True,
)

