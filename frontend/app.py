import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="MediRec AI", page_icon="🩺", layout="wide")

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
    .main { background-color: #f7f9fc; }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        border: none;
    }
    .stButton>button:hover { background-color: #1d4ed8; }
        .card {
        background-color: white;
        color: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .card h3, .card p, .card li { color: #1e293b !important; }
    .disease-header {
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .disease-header h2 { color: white; margin: 0; }
        .ai-box {
        background-color: #eff6ff;
        color: #1e293b;
        border-left: 4px solid #2563eb;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        line-height: 1.6;
    }
    section[data-testid="stSidebar"] {
        background-color: #111827;
    }
    section[data-testid="stSidebar"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
st.sidebar.markdown("## 🩺 MediRec AI")
st.sidebar.caption("ML + AI powered health assistant")
st.sidebar.divider()
page = st.sidebar.radio("Navigate", ["🔍 Symptom Checker", "📜 History", "📊 Dashboard"])

# ---------------- Symptom Checker ----------------
if page == "🔍 Symptom Checker":
    st.markdown("<h1 style='text-align:center;'>Medicine Recommendation System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Select your symptoms for an AI-assisted preliminary assessment</p>", unsafe_allow_html=True)
    st.write("")

    try:
        all_symptoms = requests.get(f"{API_URL}/symptoms").json()
    except requests.exceptions.ConnectionError:
        st.error("Backend not reachable. Make sure `uvicorn backend.main:app --reload` is running.")
        st.stop()

    col_input, _ = st.columns([2, 1])
    with col_input:
        selected_symptoms = st.multiselect(
            "Select your symptoms:",
            options=all_symptoms,
            placeholder="Start typing to search symptoms..."
        )
        predict_clicked = st.button("🔎 Analyze Symptoms", type="primary", use_container_width=True)

    if predict_clicked:
        if not selected_symptoms:
            st.warning("Please select at least one symptom.")
        else:
            with st.spinner("Analyzing symptoms..."):
                response = requests.post(f"{API_URL}/predict", json={"symptoms": selected_symptoms})

            if response.status_code == 200:
                data = response.json()

                st.markdown(f"""
                <div class="disease-header">
                    <h2>🎯 {data['predicted_disease']}</h2>
                    <p style="margin-top:0.5rem; opacity:0.9;">{data['description']}</p>
                </div>
                """, unsafe_allow_html=True)

                precautions_html = "".join([f"<li>{p}</li>" for p in data["precautions"]])
                medications_html = "".join([f"<li>{m}</li>" for m in data["medications"]])
                diet_html = "".join([f"<li>{d}</li>" for d in data["diet"]])
                workout_html = "".join([f"<li>{w}</li>" for w in data["workout"]])

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="card">
                        <h3>⚠️ Precautions</h3>
                        <ul>{precautions_html}</ul>
                    </div>
                    <div class="card">
                        <h3>💊 Medications</h3>
                        <ul>{medications_html}</ul>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="card">
                        <h3>🥗 Recommended Diet</h3>
                        <ul>{diet_html}</ul>
                    </div>
                    <div class="card">
                        <h3>🏃 Workout</h3>
                        <ul>{workout_html}</ul>
                    </div>
                    """, unsafe_allow_html=True)

                if data.get("ai_summary"):
                    st.markdown(f"""
                    <div class="ai-box">
                        <h3 style="margin-top:0;">🤖 AI-Generated Explanation</h3>
                        <p style="margin-bottom:0;">{data['ai_summary']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.session_state["last_prediction_id"] = data["id"]
            else:
                st.error(f"Prediction failed: {response.text}")

    if "last_prediction_id" in st.session_state:
        st.divider()
        st.markdown("**Was this prediction helpful?**")
        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if st.button("👍 Yes"):
                requests.post(f"{API_URL}/feedback", json={
                    "prediction_id": st.session_state["last_prediction_id"],
                    "was_helpful": True
                })
                st.toast("Thanks for your feedback!")
        with col2:
            if st.button("👎 No"):
                requests.post(f"{API_URL}/feedback", json={
                    "prediction_id": st.session_state["last_prediction_id"],
                    "was_helpful": False
                })
                st.toast("Thanks for your feedback!")

# ---------------- History ----------------
elif page == "📜 History":
    st.title("📜 Prediction History")
    history = requests.get(f"{API_URL}/history").json()
    if not history:
        st.info("No predictions yet — try the Symptom Checker first.")
    else:
        for item in history:
            st.markdown(f"""
            <div class="card">
                <strong style="font-size:1.1rem;">{item['predicted_disease']}</strong><br>
                <span style="color:gray;">Symptoms: {item['symptoms']}</span><br>
                <span style="color:#9ca3af; font-size:0.85rem;">{item['created_at']}</span>
            </div>
            """, unsafe_allow_html=True)

# ---------------- Dashboard ----------------
elif page == "📊 Dashboard":
    st.title("📊 Analytics Dashboard")
    stats = requests.get(f"{API_URL}/stats").json()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="card" style="text-align:center;">
            <p style="color:gray; margin-bottom:0.2rem;">Total Predictions Made</p>
            <h1 style="color:#2563eb; margin:0;">{stats['total_predictions']}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown("### Most Commonly Predicted Diseases")
    if stats["top_diseases"]:
        diseases = [d[0] for d in stats["top_diseases"]]
        counts = [d[1] for d in stats["top_diseases"]]
        st.bar_chart(dict(zip(diseases, counts)))
    else:
        st.info("Not enough data yet — make a few predictions first.")