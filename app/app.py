import streamlit as st
import pandas as pd
from datetime import date
import joblib
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="🚲 Bike Rental Demand Predictor",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    h1 {
        color: #2c3e50;
        font-size: 36px;
    }
    .stButton > button {
        background-color: #2e86de;
        color: white;
        font-size: 16px;
        border-radius: 10px;
        padding: 10px 20px;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #1e6bb8;
    }
    .card {
        background-color: #ffffff;
        color: #2d3436;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #0984e3;
        margin-top: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .card h3 {
        font-size: 24px;
        margin: 0;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Load model
model = joblib.load('../model/xgboost_model.pkl')

# Title
st.markdown("<h1>🚲 Bike Rental Demand Predictor</h1>", unsafe_allow_html=True)
st.markdown("""
Use the form below to predict bike demand based on weather and date inputs.  
Simply fill in the conditions and click **Predict Bike Demand**!
""")

st.markdown("---")


st.subheader("🔧 Input Parameters")
col1, col2 = st.columns(2)

with col1:
    hour = st.slider("🕒 Hour of the Day", 0, 23, 12)
    temp = st.number_input("🌡️ Temperature (°C)", value=20.0, step=0.1)
    season = st.selectbox("🍂 Season", [("Spring",1), ("Summer",2), ("Fall",3), ("Winter",4)],
                          format_func=lambda x: x[0])
    workingday_str = st.selectbox("💼 Is it a Working Day?", ["No", "Yes"])
    workingday = 1 if workingday_str == "Yes" else 0

with col2:
    weather_options = [
        ("☀️ Clear", 1),
        ("🌫️ Mist / Cloudy", 2),
        ("🌧️ Light Rain / Snow", 3),
        ("⛈️ Heavy Rain / Snow", 4)
    ]
    weather = st.selectbox("🌦️ Weather Condition", weather_options, format_func=lambda x: x[0])

    selected_date = st.date_input("📅 Select Date", min_value=date.today())
    day = selected_date.day
    year = selected_date.year

    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    current_year = date.today().year
    current_month = date.today().month
    available_months = months[current_month - 1:] if year == current_year else months

    month_name = st.selectbox("🗓️ Month", available_months)
    month = months.index(month_name) + 1

model_year = year - 2011


st.markdown("---")
st.subheader("📊 Prediction Output")

if st.button("🔍 Predict Bike Demand"):
    input_df = pd.DataFrame([{
        'season': season[1],
        'workingday': workingday,
        'weather': weather[1],
        'temp': temp,
        'hour': hour,
        'day': day,
        'year': model_year,
        'month': month
    }])

    try:
        prediction = int(model.predict(input_df)[0])
        st.markdown(f"""
            <div class="card">
                <h3>🚴 Estimated Rentals: <strong>{prediction}</strong> bikes</h3>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📊 Input Summary Visualization")

        input_for_plot = {
            'Hour': hour,
            'Temperature (°C)': temp,
            'Season': season[1],
            'Working Day': workingday,
            'Weather': weather[1],
            'Day': day,
            'Month': month,
            'Year': model_year
        }

        vis_df = pd.DataFrame({
            'Parameter': list(input_for_plot.keys()),
            'Value': list(input_for_plot.values())
        })

        st.bar_chart(vis_df.set_index('Parameter'))

        # Radar Chart
        st.markdown("#### 🕸️ Input Parameters Radar Chart")

        categories = list(input_for_plot.keys())
        values = list(input_for_plot.values())

        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
        ax.plot(angles, values, color='blue', linewidth=1, linestyle='dashed')
        ax.fill(angles, values, color='skyblue', alpha=0.4)
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=7, rotation=45)
        # ax.set_title("Input Parameters Radar Chart", fontsize=16, color='darkblue', pad=20)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Prediction failed: {e}")
