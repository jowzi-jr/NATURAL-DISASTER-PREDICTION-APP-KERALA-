import streamlit as st
import joblib
import pandas as pd
from datetime import datetime
from apis.Open_Mateo import get_weather

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Kerala Disaster Prediction",
    page_icon="🌍",
    layout="wide"
)

# -----------------------------
# Load ML Files
# -----------------------------
@st.cache_resource
def load_models():
    model = joblib.load("models/disaster_model.pkl")
    encoders = joblib.load("models/encoders.pkl")
    feature_cols = joblib.load("models/feature_cols.pkl")
    return model, encoders, feature_cols

model, encoders, feature_cols = load_models()

# -----------------------------
# Geography & Mappings
# -----------------------------
DISTRICTS = {
    "Thiruvananthapuram": (8.5241, 76.9366), "Kollam": (8.8932, 76.6141),
    "Pathanamthitta": (9.2648, 76.7870), "Alappuzha": (9.4981, 76.3388),
    "Kottayam": (9.5916, 76.5222), "Idukki": (9.8490, 76.9720),
    "Ernakulam": (9.9816, 76.2999), "Thrissur": (10.5276, 76.2144),
    "Palakkad": (10.7867, 76.6548), "Malappuram": (11.0732, 76.0740),
    "Kozhikode": (11.2588, 75.7804), "Wayanad": (11.6854, 76.1320),
    "Kannur": (11.8745, 75.3704), "Kasaragod": (12.4996, 74.9869)
}

# Reverse mapping based on your notebook's logic
DISTRICT_TO_LOCATION = {
    'Wayanad': 'mountain', 'Idukki': 'mountain', 'Palakkad': 'mountain',
    'Alappuzha': 'coastal', 'Ernakulam': 'coastal', 'Kozhikode': 'coastal', 'Kollam': 'coastal', 'Thiruvananthapuram': 'coastal',
    'Malappuram': 'inland', 'Kottayam': 'inland', 'Thrissur': 'inland', 'Kannur': 'inland', 'Pathanamthitta': 'inland', 'Kasaragod': 'inland'
}

# -----------------------------
# Helper Functions for Categorization
# -----------------------------
def get_current_season():
    month = datetime.now().month
    if month in [3, 4, 5]: return 'Pre-Monsoon'
    elif month in [6, 7, 8, 9, 10]: return 'Monsoon'
    else: return 'Summer'

def map_weather_code(code):
    if code <= 3: return 'Sunny'
    elif code <= 49: return 'Cloudy'
    else: return 'Rainy'

def map_cloud_cover(percent):
    if percent < 30: return 'clear'
    elif percent < 70: return 'partly cloudy'
    else: return 'overcast'

def safe_encode(encoder_name, value):
    try:
        return encoders[encoder_name].transform([value])[0]
    except ValueError:
        return 0 # Fallback for unseen labels

# -----------------------------
# Sidebar & Navigation
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Menu", ["Home", "Prediction", "Weather", "Emergency"])

# -----------------------------
# Home Page
# -----------------------------
if page == "Home":
    st.title("🌍 Kerala Disaster Prediction System")
    st.write("AI-powered Natural Disaster Prediction Dashboard for Kerala")

    district = st.selectbox("Select District", list(DISTRICTS.keys()))
    latitude, longitude = DISTRICTS[district]

    with st.spinner("Fetching live weather data..."):
        weather = get_weather(latitude, longitude)

    st.subheader("Current Weather")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Temperature", f"{weather['temperature']:.1f} °C")
    col2.metric("Humidity", f"{weather['humidity']:.0f}%")
    col3.metric("Wind Speed", f"{weather['wind_speed']:.1f} km/h")
    col4.metric("Precipitation", f"{weather['precipitation']:.1f} mm")

    st.divider()

    if st.button("Predict Disaster Risk", type="primary"):
        with st.spinner("Analyzing multi-hazard risk factors..."):
            try:
                # 1. Map raw API data to Categorical values expected by encoders
                location_cat = DISTRICT_TO_LOCATION.get(district, 'inland')
                season_cat = get_current_season()
                weather_type_cat = map_weather_code(weather['weather_code'])
                cloud_cover_cat = map_cloud_cover(weather['cloud_cover_percent'])

                # 2. Build the final feature dictionary matching `feature_cols` exactly
                input_data = {
                    'Temperature': weather['temperature'],
                    'Humidity': weather['humidity'],
                    'Wind Speed': weather['wind_speed'],
                    'Precipitation (%)': weather['precipitation'] * 10, # Scaling mm up to simulate the % range from notebook
                    'Atmospheric Pressure': weather['pressure'],
                    'UV Index': weather['uv_index'],
                    'Visibility (km)': weather['visibility_km'],
                    'Cloud Cover_enc': safe_encode('Cloud Cover', cloud_cover_cat),
                    'Season_enc': safe_encode('Season', season_cat),
                    'Location_enc': safe_encode('Location', location_cat),
                    'Weather Type_enc': safe_encode('Weather Type', weather_type_cat)
                }
                
                # 3. Create DataFrame and enforce column order
                input_df = pd.DataFrame([input_data])
                final_features = input_df[feature_cols]
                
                # 4. Predict
                prediction = model.predict(final_features)[0]
                probabilities = model.predict_proba(final_features)[0]
                confidence = round(float(probabilities.max()) * 100, 1)

                # 5. Display Results
                st.subheader("Risk Assessment Results")
                
                if prediction == 'Normal':
                    st.success(f"✅ **Status: Normal** (Confidence: {confidence}%)")
                    st.write(f"Current conditions in {district} do not indicate an immediate disaster threat.")
                elif prediction == 'Flood':
                    st.error(f"🌊 **HIGH ALERT: Flood Risk** (Confidence: {confidence}%)")
                    st.write("Heavy precipitation and high humidity detected. Monitor local water levels closely.")
                elif prediction == 'Landslide':
                    st.error(f"⛰️ **CRITICAL ALERT: Landslide Risk** (Confidence: {confidence}%)")
                    st.write("Saturated soil conditions and high winds in mountainous terrain detected. Evacuate vulnerable slopes.")
                elif prediction == 'Thunderstorm':
                    st.warning(f"⛈️ **WARNING: Severe Thunderstorm** (Confidence: {confidence}%)")
                    st.write("High wind speeds and atmospheric instability detected. Stay indoors.")
                elif prediction == 'Heat Wave':
                    st.warning(f"🌡️ **WARNING: Heat Wave** (Confidence: {confidence}%)")
                    st.write("Extreme temperatures and UV levels detected. Avoid prolonged sun exposure.")

            except Exception as e:
                st.error(f"An error occurred during prediction: {e}")

# -----------------------------
# Other Pages
# -----------------------------
elif page == "Prediction":
    st.header("Prediction History & Trends")
    st.info("Historical prediction logs will be shown here in a future update.")

elif page == "Weather":
    st.header("Detailed Weather Radar")
    st.info("Extended weather forecasting details will be shown here.")

elif page == "Emergency":
    st.header("Emergency Contacts - Kerala")
    st.error("🚓 Police : 100")
    st.error("🚒 Fire Force : 101")
    st.error("🚑 Ambulance : 108")
    st.error("🚨 State Disaster Management Authority (KSDMA) : 1077")