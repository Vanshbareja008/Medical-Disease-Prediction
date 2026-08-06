import os
import sqlite3
import hashlib
from datetime import datetime
import gradio as gr
import joblib
import numpy as np

# --- CONFIGURATION ---
DB_FILE = "users.db"
ADMIN_SECRET_KEY = "admin@123"

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lab_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            test_type TEXT NOT NULL,
            result_summary TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, confirm_password):
    username = username.strip()
    if not username or not password:
        return "❌ Username and password cannot be empty."
    if password != confirm_password:
        return "❌ Passwords do not match."
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                       (username, hash_password(password)))
        conn.commit()
        conn.close()
        return "✅ Account created! Please Sign In."
    except sqlite3.IntegrityError:
        return "❌ Username already exists."

def verify_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username.strip(),))
    row = cursor.fetchone()
    conn.close()
    return True if row and row[0] == hash_password(password) else False

# --- SAVE USER DIAGNOSTIC RECORD ---
def save_user_record(username, test_type, result_summary):
    if not username:
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO lab_history (username, test_type, result_summary, timestamp) VALUES (?, ?, ?, ?)",
        (username, test_type, result_summary, time_str)
    )
    conn.commit()
    conn.close()

def get_user_history(username):
    if not username:
        return []
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT test_type, result_summary, timestamp FROM lab_history WHERE username = ? ORDER BY id DESC", (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_dashboard_counts(username):
    if not username:
        return 0, 0, 0, 0
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM lab_history WHERE username = ?", (username,))
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM lab_history WHERE username = ? AND test_type = 'Heart Disease'", (username,))
    heart = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM lab_history WHERE username = ? AND test_type = 'Diabetes Analysis'", (username,))
    diabetes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM lab_history WHERE username = ? AND test_type = 'Kidney Function'", (username,))
    kidney = cursor.fetchone()[0]
    conn.close()
    return total, heart, diabetes, kidney

# --- ADMIN DATABASE FUNCTIONS ---
def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_user_by_username(username_to_delete):
    username_to_delete = username_to_delete.strip()
    if not username_to_delete:
        return "❌ Please enter a valid username."
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username_to_delete,))
    cursor.execute("DELETE FROM lab_history WHERE username = ?", (username_to_delete,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted_count > 0:
        return f"✅ User '{username_to_delete}' deleted."
    return "❌ User not found."

# --- LOAD MODELS ---
heart_model = joblib.load("heart diagn.pkl")
diabetes_model = joblib.load("diabetes diagn.pkl")
kidney_model = joblib.load("kidney diagn.pkl")
liver_model = joblib.load("Liver Diagn.pkl")
obesity_model = joblib.load("Obesity Diagn.pkl")

# --- UI VISUAL RESULT & INTERACTIVE DETAIL CARD ---
def create_interactive_result_card(title, value_text, status_label, bar_percent, recommendation, key_biomarkers, is_risk=False):
    bar_color = "#FF4C6A" if is_risk else "#22C55E"
    badge_bg = "rgba(255, 76, 106, 0.2)" if is_risk else "rgba(34, 197, 94, 0.2)"
    badge_color = "#FF4C6A" if is_risk else "#22C55E"

    return f"""
    <div style="background: #1F2238; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 20px; margin-top: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-weight: 700; color: #FFFFFF; font-size: 1.1rem;">🧪 {title}</span>
            <span style="background: {badge_bg}; color: {badge_color}; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.8rem;">
                {status_label}
            </span>
        </div>
        <div style="font-size: 1.4rem; font-weight: 800; color: #FFFFFF; margin-bottom: 14px;">
            {value_text}
        </div>
        <!-- STATUS BAR -->
        <div style="width: 100%; background: #121422; height: 10px; border-radius: 6px; overflow: hidden;">
            <div style="width: {bar_percent}%; background: {bar_color}; height: 100%; border-radius: 6px; transition: width 0.6s ease;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #9CA3AF; margin-top: 8px;">
            <span>Low Risk</span>
            <span>Moderate</span>
            <span>Elevated Risk</span>
        </div>
        
        <!-- DETAILED INTERACTION PANEL -->
        <details style="margin-top: 16px; background: #121422; border-radius: 14px; padding: 12px; color: #D1D5DB;">
            <summary style="cursor: pointer; font-weight: 700; color: #5B61F6; font-size: 0.9rem;">
                🔍 Click for Detailed Diagnostic Breakdown & Clinical Guidance
            </summary>
            <div style="margin-top: 10px; font-size: 0.85rem; line-height: 1.5;">
                <p style="margin-bottom: 6px;"><strong>Key Biomarkers Evaluated:</strong> {key_biomarkers}</p>
                <p style="margin-bottom: 0;"><strong>Clinical Recommendation:</strong> {recommendation}</p>
            </div>
        </details>
    </div>
    """

# --- PREDICTION FUNCTIONS ---
def predict_heart(username, age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal):
    data = np.array([[float(age), float(sex), float(cp), float(trestbps), float(chol),
                      float(fbs), float(restecg), float(thalach), float(exang), 
                      float(oldpeak), float(slope), float(ca), float(thal)]])
    res = heart_model.predict(data)[0]
    result_text = "Heart Disease Risk Detected" if res == 1 else "Normal Cardiac Profile"
    save_user_record(username, "Heart Disease", result_text)
    
    biomarkers = f"Cholesterol: {chol} mg/dl | Resting BP: {trestbps} mm Hg | Max HR: {thalach} bpm"
    rec = "Consult with a cardiologist for an ECG follow-up and lipid panel analysis." if res == 1 else "Maintain regular cardiovascular exercises and annual health screenings."
    
    return create_interactive_result_card("Heart Assessment", result_text, "High Risk" if res == 1 else "Optimal", 85 if res == 1 else 15, rec, biomarkers, is_risk=(res == 1))

def predict_diabetes(username, gender, age, hypertension, heart_disease, smoking, bmi, hba1c, glucose):
    gender_map = {"Female": 0, "Male": 1, "Other": 2}
    smoke_map = {"Never": 0, "No Info": 1, "Current": 2, "Former": 3, "Ever": 4, "Not Current": 5}
    data = np.array([[gender_map[gender], float(age), float(hypertension), float(heart_disease),
                      smoke_map[smoking], float(bmi), float(hba1c), float(glucose)]])
    res = diabetes_model.predict(data)[0]
    result_text = "Elevated Glucose Indicators" if res == 1 else "Normal Glycemic Profile"
    save_user_record(username, "Diabetes Analysis", result_text)
    
    biomarkers = f"HbA1c: {hba1c}% | Blood Glucose: {glucose} mg/dL | BMI: {bmi}"
    rec = "Schedule an oral glucose tolerance test and consult an endocrinologist." if res == 1 else "Maintain balanced glycemic diet and monitor glucose annually."
    
    return create_interactive_result_card("Diabetes Assessment", result_text, "High Risk" if res == 1 else "In-Range", 90 if res == 1 else 20, rec, biomarkers, is_risk=(res == 1))

def predict_kidney(username, age, gender, bp, creatinine, urea, hb, rbc, hypertension, egfr, albumin):
    data = np.array([[float(age), 1 if gender == "Male" else 0, float(bp), float(creatinine),
                      float(urea), float(hb), float(rbc), 1 if hypertension == "Yes" else 0,
                      float(egfr), 1 if albumin == "Yes" else 0]])
    res = kidney_model.predict(data)[0]
    result_text = "Kidney Disease Marker" if res == 1 else "Healthy Renal Indicators"
    save_user_record(username, "Kidney Function", result_text)
    
    biomarkers = f"eGFR: {egfr} | Serum Creatinine: {creatinine} mg/dL | Blood Urea: {urea}"
    rec = "Nephrology consult advised to check renal function and fluid levels." if res == 1 else "Renal markers within healthy baseline limits."
    
    return create_interactive_result_card("Kidney Panel", result_text, "Action Required" if res == 1 else "Optimal", 80 if res == 1 else 10, rec, biomarkers, is_risk=(res == 1))

def predict_liver(username, age, gender, tb, db, alk, sgpt, sgot, proteins, albumin, ratio):
    data = np.array([[float(age), 1 if gender == "Male" else 0, float(tb), float(db),
                      float(alk), float(sgpt), float(sgot), float(proteins), float(albumin), float(ratio)]])
    res = liver_model.predict(data)[0]
    result_text = "Hepatic Risk Indicator" if res == 1 else "Healthy Liver Function"
    save_user_record(username, "Liver Function", result_text)
    
    biomarkers = f"Total Bilirubin: {tb} | SGPT/ALT: {sgpt} | SGOT/AST: {sgot}"
    rec = "Perform liver ultrasound and evaluate enzyme levels with your clinician." if res == 1 else "Hepatic enzyme levels within baseline parameters."
    
    return create_interactive_result_card("Liver Function", result_text, "Elevated" if res == 1 else "In-Range", 75 if res == 1 else 15, rec, biomarkers, is_risk=(res == 1))

def predict_obesity(username, gender, age, height, weight, family, favc, fcvc, ncp, caec, smoke, ch2o, scc, faf, tue, calc, mtrans):
    gender_map, yesno = {"Female": 0, "Male": 1}, {"No": 0, "Yes": 1}
    caec_map = calc_map = {"No": 0, "Sometimes": 1, "Frequently": 2, "Always": 3}
    mtrans_map = {"Public Transportation": 0, "Walking": 1, "Automobile": 2, "Motorbike": 3, "Bike": 4}
    label_map = {0: "Insufficient Weight", 1: "Normal Weight", 2: "Overweight Level I", 3: "Overweight Level II", 4: "Obesity Type I", 5: "Obesity Type II", 6: "Obesity Type III"}
    
    data = np.array([[gender_map[gender], float(age), float(height), float(weight), yesno[family], yesno[favc],
                      float(fcvc), float(ncp), caec_map[caec], yesno[smoke], float(ch2o), yesno[scc],
                      float(faf), float(tue), calc_map[calc], mtrans_map[mtrans]]])
    val = int(obesity_model.predict(data)[0])
    lbl = label_map[val]
    save_user_record(username, "Body Mass", lbl)
    
    is_risk = val > 1
    pct = min(100, max(15, val * 16))
    biomarkers = f"Height: {height}m | Weight: {weight}kg | Activity Rating: {faf}/3"
    rec = "Consult with a nutritionist to establish a structured dietary and exercise plan." if is_risk else "Maintain healthy dietary habits and daily physical activities."
    
    return create_interactive_result_card("Body Mass Index", f"Category: {lbl}", "Complete", pct, rec, biomarkers, is_risk=is_risk)

# --- NAVIGATION HANDLERS ---
def handle_user_login(username, password):
    if verify_user(username, password):
        user_hist = get_user_history(username)
        t, h, d, k = get_dashboard_counts(username)
        welcome_html = f"""
        <div style="background: linear-gradient(135deg, #5B61F6 0%, #3F44D1 100%); border-radius: 20px; padding: 24px; color: #FFFFFF; display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800;">Welcome, Dr. {username}</h2>
                <p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 1rem;">Have a productive day at your AI Diagnostic Workstation.</p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 12px 20px; border-radius: 14px; font-weight: 700; text-align: right;">
                📅 Today: {datetime.now().strftime('%b %d, %Y')}
            </div>
        </div>
        """
        metrics_html = f"""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 16px;">
            <div style="background: #1F2238; border-radius: 16px; padding: 16px; text-align: center;">
                <div style="font-size: 1.8rem;">👤</div>
                <div style="color: #9CA3AF; font-size: 0.85rem; margin-top: 4px;">Total Diagnostics</div>
                <div style="color: #FFFFFF; font-size: 1.5rem; font-weight: 800;">{t}</div>
            </div>
            <div style="background: #1F2238; border-radius: 16px; padding: 16px; text-align: center;">
                <div style="font-size: 1.8rem;">❤️</div>
                <div style="color: #9CA3AF; font-size: 0.85rem; margin-top: 4px;">Heart Tests</div>
                <div style="color: #FFFFFF; font-size: 1.5rem; font-weight: 800;">{h}</div>
            </div>
            <div style="background: #1F2238; border-radius: 16px; padding: 16px; text-align: center;">
                <div style="font-size: 1.8rem;">🩸</div>
                <div style="color: #9CA3AF; font-size: 0.85rem; margin-top: 4px;">Diabetes Tests</div>
                <div style="color: #FFFFFF; font-size: 1.5rem; font-weight: 800;">{d}</div>
            </div>
            <div style="background: #1F2238; border-radius: 16px; padding: 16px; text-align: center;">
                <div style="font-size: 1.8rem;">🫘</div>
                <div style="color: #9CA3AF; font-size: 0.85rem; margin-top: 4px;">Kidney Tests</div>
                <div style="color: #FFFFFF; font-size: 1.5rem; font-weight: 800;">{k}</div>
            </div>
        </div>
        """
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), "", username, user_hist, welcome_html, metrics_html
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "❌ Invalid username or password.", "", [], "", ""

def handle_admin_login(passcode):
    if passcode == ADMIN_SECRET_KEY:
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), "", "", [], "", "", get_all_users()
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "❌ Incorrect Admin Secret Key.", "", [], "", "", []

def handle_logout():
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "", "", [], "", ""

# --- DARK DASHBOARD CSS ---
css = """
:root {
    --bg-main: #121422;
    --card-bg: #1A1D2E;
    --accent-blue: #5B61F6;
    --text-primary: #FFFFFF;
    --text-secondary: #9CA3AF;
    --border-color: #2D314E;
}

body, .gradio-container {
    background-color: var(--bg-main) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

.dark-dashboard-card {
    background: var(--card-bg) !important;
    border-radius: 24px !important;
    padding: 24px !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: 0 12px 32px rgba(0,0,0,0.4) !important;
}

.scroll-panel {
    max-height: 520px;
    overflow-y: auto !important;
    padding-right: 8px;
}

.scroll-panel::-webkit-scrollbar { width: 6px; }
.scroll-panel::-webkit-scrollbar-thumb { background: #374151; border-radius: 10px; }

button[role="tab"] {
    color: var(--text-secondary) !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    background: transparent !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 18px !important;
}

button[role="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    background: var(--accent-blue) !important;
}

label span { color: var(--text-primary) !important; font-weight: 600 !important; font-size: 0.85rem !important; }
input, select, textarea {
    background-color: #121422 !important;
    color: #FFFFFF !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    padding: 10px 12px !important;
}

button.primary-btn {
    background: var(--accent-blue) !important;
    color: #FFFFFF !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 12px !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(91, 97, 246, 0.4) !important;
    cursor: pointer;
    margin-top: 12px;
}

button.logout-btn {
    background: #2D314E !important;
    color: #FF4C6A !important;
    border: 1px solid #FF4C6A !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
}

footer { visibility: hidden !important; }
"""

with gr.Blocks(css=css, title="Sick Sense Clinical Dashboard") as demo:
    current_user_state = gr.State(value="")

    # ------------------ AUTHENTICATION PORTAL ------------------
    with gr.Column(visible=True, elem_classes=["dark-dashboard-card"]) as auth_view:
        gr.Markdown("## 🏥 Sick Sense Clinical Portal")
        with gr.Tabs():
            with gr.Tab("Sign In"):
                username_input = gr.Textbox(label="Username", placeholder="Enter username")
                password_input = gr.Textbox(label="Password", type="password", placeholder="Enter password")
                login_btn = gr.Button("Sign In to Dashboard", elem_classes=["primary-btn"])
                login_msg = gr.Markdown("")

            with gr.Tab("Register"):
                new_username = gr.Textbox(label="New Username", placeholder="Choose username")
                new_password = gr.Textbox(label="New Password", type="password", placeholder="Choose password")
                confirm_password = gr.Textbox(label="Confirm Password", type="password", placeholder="Re-enter password")
                signup_btn = gr.Button("Create Account", elem_classes=["primary-btn"])
                signup_msg = gr.Markdown("")

            with gr.Tab("🛡️ Admin Portal"):
                admin_key_input = gr.Textbox(label="Admin Passcode", type="password", placeholder="Enter admin passcode")
                admin_login_btn = gr.Button("Access Admin Panel", elem_classes=["primary-btn"])
                admin_msg = gr.Markdown("")

    # ------------------ MAIN CLINICAL DASHBOARD ------------------
    with gr.Row(visible=False, elem_classes=["dark-dashboard-card"]) as user_dashboard_view:
        # LEFT SIDEBAR NAVIGATION
        with gr.Column(scale=1, min_width=180):
            gr.Markdown("### 🏥 **Sick Sense**")
            gr.Markdown("---")
            gr.Markdown("🏠 **Dashboard**")
            gr.Markdown("📅 **Appointments**")
            gr.Markdown("📊 **Reports**")
            gr.Markdown("⚙️ **Settings**")
            gr.Markdown("---")
            user_logout_btn = gr.Button("Sign Out", elem_classes=["logout-btn"])

        # MAIN CONTENT AREA
        with gr.Column(scale=5):
            welcome_banner = gr.HTML()
            metrics_banner = gr.HTML()
            
            gr.Markdown("---")

            with gr.Tabs():
                # Heart Health Tab
                with gr.Tab("❤️ Heart"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        with gr.Row():
                            age = gr.Number(label="Age", value=45)
                            sex = gr.Dropdown(["0", "1"], value="1", label="Sex (1=Male, 0=Female)")
                            cp = gr.Dropdown(["0", "1", "2", "3"], value="0", label="Chest Pain Type")
                        with gr.Row():
                            trestbps = gr.Number(label="Resting BP (mm Hg)", value=130)
                            chol = gr.Number(label="Cholesterol (mg/dl)", value=250)
                            fbs = gr.Dropdown(["0", "1"], value="0", label="Fasting Sugar (>120 mg/dl)")
                        with gr.Row():
                            restecg = gr.Dropdown(["0", "1", "2"], value="1", label="Rest ECG")
                            thalach = gr.Number(label="Max Heart Rate", value=150)
                            exang = gr.Dropdown(["0", "1"], value="0", label="Exercise Angina")
                        with gr.Row():
                            oldpeak = gr.Number(label="ST Depression", value=1.2)
                            slope = gr.Dropdown(["0", "1", "2"], value="2", label="Slope")
                            ca = gr.Dropdown(["0", "1", "2", "3", "4"], value="0", label="Major Vessels")
                            thal = gr.Dropdown(["0", "1", "2", "3"], value="2", label="Thal")

                        heart_btn = gr.Button("Run Heart Diagnostics", elem_classes=["primary-btn"])
                        heart_output = gr.HTML()

                # Diabetes Tab
                with gr.Tab("🩸 Diabetes"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        with gr.Row():
                            gender = gr.Dropdown(["Female", "Male", "Other"], value="Male", label="Gender")
                            d_age = gr.Number(label="Age", value=40)
                        with gr.Row():
                            hypertension = gr.Dropdown([0, 1], value=0, label="Hypertension (0=No, 1=Yes)")
                            heart_disease = gr.Dropdown([0, 1], value=0, label="Heart Disease (0=No, 1=Yes)")
                        smoking = gr.Dropdown(["Never", "No Info", "Current", "Former", "Ever", "Not Current"], value="Never", label="Smoking History")
                        with gr.Row():
                            bmi = gr.Number(label="BMI", value=24)
                            hba1c = gr.Number(label="HbA1c Level", value=5.6)
                            glucose = gr.Number(label="Blood Glucose", value=110)

                        diabetes_btn = gr.Button("Analyze Glycemic Profile", elem_classes=["primary-btn"])
                        diabetes_output = gr.HTML()

                # Kidney Tab
                with gr.Tab("🫘 Kidney"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        with gr.Row():
                            k_age = gr.Number(label="Age", value=48)
                            k_gender = gr.Dropdown(["Male", "Female"], value="Male", label="Gender")
                            k_bp = gr.Number(label="Blood Pressure", value=80)
                        with gr.Row():
                            k_creatinine = gr.Number(label="Serum Creatinine", value=1.2)
                            k_urea = gr.Number(label="Blood Urea", value=36)
                            k_hb = gr.Number(label="Hemoglobin", value=15.4)
                        with gr.Row():
                            k_rbc = gr.Number(label="Red Blood Cells", value=5.2)
                            k_hypertension = gr.Dropdown(["No", "Yes"], value="No", label="Hypertension")
                            k_egfr = gr.Number(label="eGFR", value=90)
                            k_albumin = gr.Dropdown(["No", "Yes"], value="No", label="Albumin")

                        kidney_btn = gr.Button("Run Renal Evaluation", elem_classes=["primary-btn"])
                        kidney_output = gr.HTML()

                # Liver Tab
                with gr.Tab("🫀 Liver"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        with gr.Row():
                            l_age = gr.Number(label="Age", value=65)
                            l_gender = gr.Dropdown(["Male", "Female"], value="Male", label="Gender")
                            l_tb = gr.Number(label="Total Bilirubin", value=0.7)
                        with gr.Row():
                            l_db = gr.Number(label="Direct Bilirubin", value=0.1)
                            l_alk = gr.Number(label="Alkaline Phosphatase", value=187)
                            l_sgpt = gr.Number(label="SGPT", value=16)
                        with gr.Row():
                            l_sgot = gr.Number(label="SGOT", value=18)
                            l_proteins = gr.Number(label="Total Proteins", value=6.8)
                            l_albumin = gr.Number(label="Albumin", value=3.3)
                            l_ratio = gr.Number(label="A/G Ratio", value=0.9)

                        liver_btn = gr.Button("Analyze Liver Biomarkers", elem_classes=["primary-btn"])
                        liver_output = gr.HTML()

                # Body Mass Tab
                with gr.Tab("⚖️ Body Mass"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        with gr.Row():
                            o_gender = gr.Dropdown(["Female", "Male"], value="Male", label="Gender")
                            o_age = gr.Number(label="Age", value=21)
                            o_height = gr.Number(label="Height (m)", value=1.70)
                            o_weight = gr.Number(label="Weight (kg)", value=70)
                        with gr.Row():
                            o_family = gr.Dropdown(["No", "Yes"], value="Yes", label="Family History")
                            o_favc = gr.Dropdown(["No", "Yes"], value="Yes", label="High Calorie Food Intake")
                            o_fcvc = gr.Number(label="Vegetable Intake (1-3)", value=2)
                            o_ncp = gr.Number(label="Meals Per Day (1-4)", value=3)
                        with gr.Row():
                            o_caec = gr.Dropdown(["No", "Sometimes", "Frequently", "Always"], value="Sometimes", label="Snack Frequency")
                            o_smoke = gr.Dropdown(["No", "Yes"], value="No", label="Smoker")
                            o_ch2o = gr.Number(label="Water Intake (1-3)", value=2)
                            o_scc = gr.Dropdown(["No", "Yes"], value="No", label="Calorie Tracking")
                        with gr.Row():
                            o_faf = gr.Number(label="Physical Activity (0-3)", value=1)
                            o_tue = gr.Number(label="Screen Time (0-2)", value=1)
                            o_calc = gr.Dropdown(["No", "Sometimes", "Frequently", "Always"], value="Sometimes", label="Alcohol Intake")
                            o_mtrans = gr.Dropdown(["Public Transportation", "Walking", "Automobile", "Motorbike", "Bike"], value="Public Transportation", label="Transportation")

                        obesity_btn = gr.Button("Analyze Mass Profile", elem_classes=["primary-btn"])
                        obesity_output = gr.HTML()

                # History Tab
                with gr.Tab("📜 Medical History Log"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        history_table = gr.Dataframe(headers=["Test Module", "Outcome Result", "Date & Time"], value=[], interactive=False)
                        refresh_history_btn = gr.Button("🔄 Refresh Medical History Records")

    # ------------------ ADMIN PANEL PAGE ------------------
    with gr.Column(visible=False, elem_classes=["dark-dashboard-card"]) as admin_dashboard_view:
        with gr.Row():
            gr.Markdown("### 🛡️ Admin User Database Portal")
            admin_logout_btn = gr.Button("Exit Panel", elem_classes=["logout-btn"], scale=0, min_width=100)

        with gr.Column(elem_classes=["scroll-panel"]):
            user_table = gr.Dataframe(headers=["User ID", "Username"], value=[], interactive=False)
            refresh_btn = gr.Button("🔄 Refresh Database Records")

            gr.Markdown("---")
            gr.Markdown("#### Delete Account Record")
            with gr.Row():
                user_to_delete = gr.Textbox(label="Target Username", placeholder="Enter username")
                delete_user_btn = gr.Button("Delete User", elem_classes=["primary-btn"])
            admin_action_msg = gr.Markdown("")

    # ------------------ EVENT LISTENERS ------------------
    signup_btn.click(register_user, inputs=[new_username, new_password, confirm_password], outputs=[signup_msg])
    login_btn.click(handle_user_login, inputs=[username_input, password_input], outputs=[auth_view, user_dashboard_view, admin_dashboard_view, login_msg, current_user_state, history_table, welcome_banner, metrics_banner])
    admin_login_btn.click(handle_admin_login, inputs=[admin_key_input], outputs=[auth_view, user_dashboard_view, admin_dashboard_view, admin_msg, current_user_state, history_table, welcome_banner, metrics_banner, user_table])
    
    user_logout_btn.click(handle_logout, inputs=[], outputs=[auth_view, user_dashboard_view, admin_dashboard_view, username_input, password_input, history_table, current_user_state])
    admin_logout_btn.click(handle_logout, inputs=[], outputs=[auth_view, user_logout_btn, admin_dashboard_view, admin_key_input, admin_msg, history_table, current_user_state])
    
    refresh_history_btn.click(get_user_history, inputs=[current_user_state], outputs=[history_table])
    refresh_btn.click(get_all_users, inputs=[], outputs=[user_table])
    delete_user_btn.click(delete_user_by_username, inputs=[user_to_delete], outputs=[admin_action_msg]).then(get_all_users, inputs=[], outputs=[user_table])

    # Model Execution Handlers
    heart_btn.click(predict_heart, inputs=[current_user_state, age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal], outputs=heart_output).then(get_user_history, inputs=[current_user_state], outputs=[history_table])
    diabetes_btn.click(predict_diabetes, inputs=[current_user_state, gender, d_age, hypertension, heart_disease, smoking, bmi, hba1c, glucose], outputs=diabetes_output).then(get_user_history, inputs=[current_user_state], outputs=[history_table])
    kidney_btn.click(predict_kidney, inputs=[current_user_state, k_age, k_gender, k_bp, k_creatinine, k_urea, k_hb, k_rbc, k_hypertension, k_egfr, k_albumin], outputs=kidney_output).then(get_user_history, inputs=[current_user_state], outputs=[history_table])
    liver_btn.click(predict_liver, inputs=[current_user_state, l_age, l_gender, l_tb, l_db, l_alk, l_sgpt, l_sgot, l_proteins, l_albumin, l_ratio], outputs=liver_output).then(get_user_history, inputs=[current_user_state], outputs=[history_table])
    obesity_btn.click(predict_obesity, inputs=[current_user_state, o_gender, o_age, o_height, o_weight, o_family, o_favc, o_fcvc, o_ncp, o_caec, o_smoke, o_ch2o, o_scc, o_faf, o_tue, o_calc, o_mtrans], outputs=obesity_output).then(get_user_history, inputs=[current_user_state], outputs=[history_table])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
