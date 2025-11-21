import streamlit as st
import streamlit as st
import requests
import json
import time
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import os
from model import predict_risk
from report_generator import generate_pdf
 
from db import (
    init_db, save_prediction, fetch_all_predictions,
    fetch_patient_history, export_patient_history_csv,
    export_all_predictions_csv
)

init_db()


import streamlit as st
import pandas as pd

st.set_page_config(page_title="Heart Health Assistant", layout="wide")

# Sidebar navigation
selected_tab = st.sidebar.radio("🧭 Navigation", [
    
    "🧪 Predict Risk",
    "📈 My History",
    "📋 All Records",
    "🩺 Cardiologist Finder",
    "📄 Doctor Summary",
    "🚨 Emergency Mode",
    "🧑‍⚕️ Doctor Mode",
    "🧑‍⚕️ chatbot",
    
    
])

if selected_tab == "🧪 Predict Risk":
    st.title("❤️ Heart Disease Risk Predictor")

    st.header("🧠 Symptom-to-Risk Mapping")
    with st.expander("Select Symptoms"):
        symptoms = st.multiselect("Choose symptoms:", [
            "💔 Chest pain", "😮‍💨 Shortness of breath", "😴 Fatigue",
            "😵 Dizziness", "🦵 Swelling in legs", "💓 Rapid heartbeat"
        ], key="symptoms_tab1")
        symptom_alert = False
        if symptoms:
            st.info("🧠 Risk Insight:")
            if "💔 Chest pain" in symptoms or "😮‍💨 Shortness of breath" in symptoms:
                st.warning("⚠️ These symptoms may indicate elevated cardiac risk.")
                symptom_alert = True
            elif "😴 Fatigue" in symptoms or "😵 Dizziness" in symptoms:
                st.write("Could be linked to circulation or rhythm issues.")
                symptom_alert = True
            else:
                st.write("Symptoms are mild, but monitoring is advised.")

    st.header("🩺 Enter Your Health Details")
    with st.expander("Fill the form below"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input(
                "Age (years)",
                min_value=1,
                max_value=120,
                step=1,
                help="Enter your age in whole years",
                key="age_tab1"
            )
            bp = st.number_input(
                "Blood Pressure (mmHg)",
                min_value=50.0,
                max_value=250.0,
                format="%.2f",
                help="Typical range: 90–140 mmHg",
                key="bp_tab1"
            )
            chol = st.number_input(
                "Cholesterol (mg/dL)",
                min_value=100.0,
                max_value=400.0,
                format="%.2f",
                help="Typical range: 125–200 mg/dL",
                key="chol_tab1"
            )
            max_hr = st.number_input(
                "Max Heart Rate",
                min_value=40.0,
                max_value=220.0,
                format="%.2f",
                help="Typical range: 100–190 bpm",
                key="maxhr_tab1"
            )

        with col2:
            ecg = st.selectbox("ECG Result", ["Normal", "Abnormal"], key="ecg_tab1")
            congenital = st.checkbox("🧬 I have a diagnosed heart hole or congenital defect", key="congenital_tab1")

            patient_name = st.text_input("Your Name", key="name_tab1")
            if patient_name and not re.match(r"^[A-Za-z ]+$", patient_name):
                st.warning("Name must contain only letters and spaces.")

            

    if st.button("🔍 Predict Risk", key="predict_button_tab1"):
        score = 0
        score += 2 if age > 55 else 1 if age > 45 else 0
        score += 2 if bp > 140 else 1 if bp > 130 else 0
        score += 2 if chol > 240 else 1 if chol > 200 else 0
        score += 1 if max_hr < 100 else 0
        score += 2 if ecg == "Abnormal" else 0

        if congenital:
            risk = "Unscored"
            disease = "Congenital Heart Defect"
            st.warning("⚠️ Risk score bypassed due to congenital condition. Please consult a cardiologist.")
        elif symptom_alert:
            risk = "Elevated"
            disease = "Possible Structural/Cardiac Issue"
            st.warning("⚠️ Symptoms suggest elevated risk. Please seek medical evaluation.")
        else:
            if score >= 7:
                risk = "High"
                disease = "Likely Coronary/Hypertensive Risk"
            elif score >= 4:
                risk = "Medium"
                disease = "Moderate Risk"
            else:
                risk = "Low"
                disease = "Minimal Risk"

        st.success(f"✅ Predicted Risk: {risk}")
        st.info(f"🩺 Disease Type: {disease}")

        st.subheader("💡 Lifestyle Recommendations")
        if risk == "High":
            st.warning("⚠️ High risk detected. Please consult a cardiologist.")
            st.write("- Reduce saturated fats and sodium")
            st.write("- Walk 30+ minutes daily")
            st.write("- Monitor BP and cholesterol regularly")
        elif risk == "Medium":
            st.info("Moderate risk. Consider lifestyle adjustments.")
            st.write("- Eat more fiber and vegetables")
            st.write("- Exercise 3–4 times a week")
            st.write("- Reduce stress and get regular checkups")
        elif risk == "Low":
            st.success("Low risk. Keep up the healthy habits!")
            st.write("- Maintain balanced diet and active lifestyle")
        else:
            st.info("Risk score not applicable. Please consult a specialist.")

        st.subheader("📊 Risk Contribution")
        fig, ax = plt.subplots()
        ax.bar(['Age', 'BP', 'Chol', 'Max HR', 'ECG'],
               [int(age > 50), int(bp > 130), int(chol > 200), int(max_hr < 100), int(ecg == "Abnormal")],
               color=['#FF9999', '#FFCC99', '#99CCFF', '#66FF99', '#FFB6C1'])
        ax.set_ylabel("Risk Score")
        ax.set_title("Risk Factor Contribution")
        st.pyplot(fig)

        save_prediction(patient_name, age, bp, chol, max_hr, ecg, risk, disease)
        filename = generate_pdf(patient_name, age, bp, chol, max_hr, ecg, {"risk": risk, "disease": disease})
        with open(filename, "rb") as f:
            st.download_button("📥 Download PDF Report", f, file_name=filename)

        

elif selected_tab == "📈 My History":
    st.title("❤️ Heart Disease Risk Predictor")

    st.header("📈 Your Health History")

    if "name_tab1" in st.session_state and st.session_state.name_tab1:
        patient_name = st.session_state.name_tab1
        history = fetch_patient_history(patient_name)

        if history:
            df = pd.DataFrame(history, columns=["Age", "BP", "Chol", "Max HR", "ECG", "Risk", "Disease", "Timestamp"])
            st.dataframe(df, use_container_width=True)

            st.line_chart(df.set_index("Timestamp")[["Chol", "BP", "Max HR"]])

            if st.button("📁 Export My History as CSV", key="export_csv_tab2"):
                csv_file = export_patient_history_csv(patient_name)
                with open(csv_file, "rb") as f:
                    st.download_button("Download CSV", f, file_name=csv_file)
        else:
            st.info("No history found for this name.")
    else:
        st.warning("Please enter your name in the Predict Risk tab to view history.")


elif selected_tab == "📋 All Records":
    st.title("❤️ Heart Disease Risk Predictor")

    st.header("📋 All Patient Records")
    records = fetch_all_predictions()
    if records:
        df = pd.DataFrame(records, columns=["Name", "Age", "BP", "Chol", "Max HR", "ECG", "Risk", "Disease", "Timestamp"])
        st.dataframe(df, use_container_width=True)

        disease_filter = st.selectbox("Filter by Disease", ["All"] + df["Disease"].unique().tolist(), key="disease_filter_tab3")
        if disease_filter != "All":
            st.dataframe(df[df["Disease"] == disease_filter], use_container_width=True)

        if st.button("📁 Export All Records as CSV", key="export_all_tab3"):
            csv_file = export_all_predictions_csv()
            with open(csv_file, "rb") as f:
                st.download_button("Download CSV", f, file_name=csv_file)

        st.subheader("📊 Disease Distribution")
        disease_counts = df["Disease"].value_counts()
        fig3, ax3 = plt.subplots()
        ax3.pie(disease_counts.values, labels=disease_counts.index, autopct='%1.1f%%', colors=plt.cm.Paired.colors)
        ax3.set_title("Disease Type Distribution")
        st.pyplot(fig3)

        st.subheader("📊 Risk Level Distribution")
        risk_counts = df["Risk"].value_counts()
        fig4, ax4 = plt.subplots()
        ax4.bar(risk_counts.index, risk_counts.values, color='skyblue')
        ax4.set_ylabel("Number of Patients")
        ax4.set_title("Risk Level Distribution")
        st.pyplot(fig4)
    else:
        st.info("No patient records available.")


elif selected_tab == "🩺 Cardiologist Finder":
    st.title("❤️ Heart Disease Risk Predictor")

    st.header("🩺 Cardiologist Finder")
    st.caption("Location-based search for heart specialists")
    city = st.text_input("Enter your city or area (e.g., Bengaluru, Mumbai)", key="city_tab5")
    if city:
        st.markdown(f"🔍 Searching for cardiologists in **{city}**...")
        st.markdown("🏥 [Nearest Hospital](https://www.google.com/maps/search/cardiologist+hospital+near+me+{city})")
        
        st.markdown(f"🗺️ [Search on Google Maps](https://www.google.com/maps/search/cardiologist+near+{city})")


    



elif selected_tab == "📄 Doctor Summary":
    st.title("❤️ Heart Disease Risk Predictor")

    name = st.text_input("Patient Name", key="name_tab8")
    age = st.number_input("Age", min_value=1, key="age_tab8")
    bp = st.number_input("Blood Pressure", key="bp_tab8")
    hr = st.number_input("Heart Rate", key="hr_tab8")
    symptoms = st.text_area("Symptoms", key="symptoms_tab8")
    meds = st.text_area("Current Medications", key="meds_tab8")

    if st.button("📝 Generate Summary", key="generate_tab8"):
        st.success("Summary ready below:")

        # 📝 Display summary
        st.markdown(f"""
        **Patient Name:** {name}  
        **Age:** {age}  
        **Blood Pressure:** {bp} mmHg  
        **Heart Rate:** {hr} bpm  
        **Symptoms:** {symptoms}  
        **Medications:** {meds}  
        """)
        st.info("✅ You can copy this summary or download it as a PDF.")

        # 📄 Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Heart Disease Risk Summary", ln=True, align="C")
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=f"""
Patient Name: {name}
Age: {age}
Blood Pressure: {bp} mmHg
Heart Rate: {hr} bpm
Symptoms: {symptoms}
Medications: {meds}
        """)

        # 🔄 Convert PDF to bytes
        pdf_output = pdf.output(dest='S').encode('latin-1')

        # 📥 Download button
        st.download_button(
            label="📥 Download PDF Summary",
            data=pdf_output,
            file_name=f"{name}_doctor_summary.pdf",
            mime="application/pdf"
        )


elif selected_tab == "🚨 Emergency Mode":
    st.header("🚨 Emergency Mode")
    st.caption("Quick access to nearby hospitals and emergency help")

    user_location = st.text_input("📍 Enter your location or area", placeholder="e.g., Indiranagar, Bengaluru", key="location_tab9")

    if user_location:
        st.success(f"Showing hospitals near **{user_location}**")

        st.markdown("### 🔗 Quick Access Links")
        st.markdown(f"- 🗺️ [Google Maps: Hospitals near {user_location}](https://www.google.com/maps/search/hospitals+near+{user_location})")
    else:
        st.info("Enter your area to find nearby hospitals and emergency options.")




elif selected_tab == "🧑‍⚕️ Doctor Mode":
    st.title("❤️ Heart Disease Risk Predictor")

    st.header("🧑‍⚕️ Doctor Mode")
    st.caption("Clinician dashboard with patient insights, notes, and live risk monitoring")

    all_patients = fetch_all_predictions()
    if all_patients:
        df = pd.DataFrame(all_patients, columns=["Name", "Age", "BP", "Chol", "Max HR", "ECG", "Risk", "Disease", "Timestamp"])
        st.subheader("📋 All Patient Records")
        st.dataframe(df, use_container_width=True)

        st.subheader("🧑‍⚕️ Patient Review")
        selected = st.selectbox("Select patient", df["Name"].unique(), key="doc_select")
        patient_data = df[df["Name"] == selected]
        st.write(patient_data)
        st.text_area("Doctor Notes", key="doc_notes")
        st.button("💾 Save Notes", key="save_notes")

        st.subheader("🚨 High-Risk Alerts")
        high_risk_df = df[df["Risk"] == "High"]
        if not high_risk_df.empty:
            st.error(f"{len(high_risk_df)} patients flagged as high risk")
            st.dataframe(high_risk_df)
        else:
            st.success("No high-risk patients at the moment.")

        st.subheader("📈 Risk Trend Over Time")
        trend_df = df.groupby("Timestamp")["Risk"].value_counts().unstack().fillna(0)
        st.line_chart(trend_df)
    else:
        st.info("No patient data available.")
        
      

# ---------------------------
# Chatbot Tab
# ---------------------------
if selected_tab == "🧑‍⚕️ chatbot":

    # ---------------------------
    # Custom CSS Styling
    # ---------------------------
    st.markdown("""
        <style>
        /* Background gradient */
        .stApp {
            background: linear-gradient(135deg, #1f1c2c, #928dab);
            font-family: 'Segoe UI', sans-serif;
        }

        /* Chat bubbles */
        .chat-bubble {
            padding: 12px 18px;
            border-radius: 18px;
            margin-bottom: 12px;
            max-width: 80%;
            line-height: 1.5;
            display: flex;
            align-items: center;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        }

        /* User bubble */
        .user-bubble {
            background-color: #4a90e2;
            color: white;
            margin-left: auto;
            justify-content: flex-end;
        }

        /* Assistant bubble */
        .assistant-bubble {
            background-color: #2c2c54;
            color: #f5f5f5;
            margin-right: auto;
            justify-content: flex-start;
        }

        /* Avatars */
        .avatar {
            font-size: 1.5em;
            margin-right: 10px;
            margin-left: 10px;
        }

        /* Title styling */
        h1 {
            text-align: center;
            color: #ffffff;
            font-size: 2.2em;
            margin-bottom: 20px;
        }

        /* Chat input box */
        .stChatInput input {
            border-radius: 12px;
            padding: 10px;
            border: 2px solid #4a90e2;
        }
        </style>
    """, unsafe_allow_html=True)

    # ---------------------------
    # App Title
    # ---------------------------
    st.title("💬 Health Assistant Chatbot ")

    # ---------------------------
    # Session State
    # ---------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ---------------------------
    # Render Chat History
    # ---------------------------
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-bubble user-bubble'><div class='avatar'>👩</div>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble assistant-bubble'><div class='avatar'>🤖</div>{msg['content']}</div>", unsafe_allow_html=True)

    # ---------------------------
    # Chat Input
    # ---------------------------
    user_input = st.chat_input("Ask me anything…")

    if user_input:
        # Show user bubble
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.markdown(f"<div class='chat-bubble user-bubble'><div class='avatar'>👩</div>{user_input}</div>", unsafe_allow_html=True)

        # Assistant bubble with streaming response
        full_reply = ""
        placeholder = st.empty()
        placeholder.markdown("<div class='chat-bubble assistant-bubble'><div class='avatar'>🤖</div>_Thinking…_</div>", unsafe_allow_html=True)
        time.sleep(0.3)
        placeholder.empty()

        try:
            # Call Ollama locally
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "mistral", "prompt": user_input},
                stream=True
            )
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        token = data.get("response", "")
                        full_reply += token
                        placeholder.markdown(f"<div class='chat-bubble assistant-bubble'><div class='avatar'>🤖</div>{full_reply}</div>", unsafe_allow_html=True)
                        if data.get("done"):
                            break
                    except Exception:
                        continue
        except Exception:
            placeholder.markdown("<div class='chat-bubble assistant-bubble'><div class='avatar'>🤖</div>⚠️ Could not connect to Ollama. Make sure it’s running.</div>", unsafe_allow_html=True)

        st.session_state.messages.append({"role": "assistant", "content": full_reply})