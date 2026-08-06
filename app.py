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
        return "❌ <span style='color: #FF5A5A; font-weight: bold;'>Username and password cannot be empty.</span>"
    if password != confirm_password:
        return "❌ <span style='color: #FF5A5A; font-weight: bold;'>Passwords do not match.</span>"
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                       (username, hash_password(password)))
        conn.commit()
        conn.close()
        return "✅ <span style='color: #22C55E; font-weight: bold;'>Account created successfully! Please Sign In.</span>"
    except sqlite3.IntegrityError:
        return "❌ <span style='color: #FF5A5A; font-weight: bold;'>Username already exists.</span>"

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
        return 0, 0, 0, 0, 0
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
    cursor.execute("SELECT COUNT(*) FROM lab_history WHERE username = ? AND test_type = 'Liver Function'", (username,))
    liver = cursor.fetchone()[0]
    conn.close()
    return total, heart, diabetes, kidney, liver

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
        return "❌ <span style='color: #FF5A5A; font-weight: bold;'>Please enter a valid username.</span>"
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username_to_delete,))
    cursor.execute("DELETE FROM lab_history WHERE username = ?", (username_to_delete,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted_count > 0:
        return f"✅ <span style='color: #22C55E; font-weight: bold;'>User '{username_to_delete}' deleted successfully.</span>"
    return "❌ <span style='color: #FF5A5A; font-weight: bold;'>User not found.</span>"

# --- LOAD MODELS ---
heart_model = joblib.load("heart diagn.pkl")
diabetes_model = joblib.load("diabetes diagn.pkl")
kidney_model = joblib.load("kidney diagn.pkl")
liver_model = joblib.load("Liver Diagn.pkl")
obesity_model = joblib.load("Obesity Diagn.pkl")

# --- HIGH-CONTRAST INTERACTIVE RESULT CARD ---
def create_interactive_result_card(title, value_text, status_label, bar_percent, recommendation, key_biomarkers, risk_level_text, is_risk=False):
    bar_color = "#FF4C6A" if is_risk else "#22C55E"
    badge_bg = "rgba(255, 76, 106, 0.25)" if is_risk else "rgba(34, 197, 94, 0.25)"
    badge_color = "#FF7A93" if is_risk else "#4ADE80"

    return f"""
    <div style="background: #1B1E32; border: 1px solid #3B426B; border-radius: 18px; padding: 22px; margin-top: 18px; box-shadow: 0 8px 24px rgba(0,0,0,0.35);">
        <!-- TOP ROW -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.3rem;">🧪</span>
                <span style="font-weight: 800; color: #FFFFFF; font-size: 1.2rem; letter-spacing: 0.3px;">{title}</span>
            </div>
            <span style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_color}; padding: 6px 16px; border-radius: 20px; font-weight: 800; font-size: 0.85rem; text-transform: uppercase;">
                {status_label}
            </span>
        </div>

        <!-- DIAGNOSIS HIGHLIGHT -->
        <div style="font-size: 1.45rem; font-weight: 800; color: #FFFFFF; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
            <span style="color: #9CA3AF; font-size: 1rem; font-weight: 600;">Status:</span> {value_text}
        </div>

        <!-- PROGRESS/RISK BAR -->
        <div style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #E5E7EB; font-weight: 700; margin-bottom: 6px;">
                <span>Risk Indicator Score</span>
                <span style="color: {badge_color};">{bar_percent}% Calculated Index</span>
            </div>
            <div style="width: 100%; background: #0F111E; height: 12px; border-radius: 6px; overflow: hidden; border: 1px solid #2A2E4B;">
                <div style="width: {bar_percent}%; background: {bar_color}; height: 100%; border-radius: 6px; transition: width 0.8s ease-in-out;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: #9CA3AF; margin-top: 6px; font-weight: 600;">
                <span>0% (Optimal Target)</span>
                <span>50% (Moderate Warning)</span>
                <span>100% (High Clinical Risk)</span>
            </div>
        </div>
        
        <!-- EXPANDABLE CLINICAL ANALYSIS PANEL -->
        <details open style="margin-top: 18px; background: #121422; border-radius: 12px; padding: 14px 18px; border: 1px solid #2D3256;">
            <summary style="cursor: pointer; font-weight: 800; color: #7C82FF; font-size: 0.95rem; user-select: none;">
                🔍 Detailed Biomarker Breakdown & Clinical Guidance
            </summary>
            <div style="margin-top: 12px; font-size: 0.9rem; color: #F3F4F6; line-height: 1.6;">
                <div style="margin-bottom: 8px; background: #1A1D2E; padding: 10px; border-radius: 8px; border-left: 4px solid #5B61F6;">
                    <strong style="color: #A5B4FC;">Key Biomarkers Evaluated:</strong><br/>
                    <span style="color: #FFFFFF; font-weight: 600;">{key_biomarkers}</span>
                </div>
                <div style="margin-bottom: 8px; background: #1A1D2E; padding: 10px; border-radius: 8px; border-left: 4px solid {bar_color};">
                    <strong style="color: #A5B4FC;">Risk Stratification:</strong><br/>
                    <span style="color: #FFFFFF; font-weight: 600;">{risk_level_text}</span>
                </div>
                <div style="background: #1A1D2E; padding: 10px; border-radius: 8px; border-left: 4px solid #22C55E;">
                    <strong style="color: #A5B4FC;">Actionable Recommendation:</strong><br/>
                    <span style="color: #FFFFFF; font-weight: 600;">{recommendation}</span>
                </div>
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
    
    biomarkers = f"Age: {age} | Resting BP: {trestbps} mm Hg | Cholesterol: {chol} mg/dl | Max Heart Rate: {thalach} bpm | ST Depression: {oldpeak}"
    risk_level = "High Probability of Cardiovascular Anomaly" if res == 1 else "Low Probability / Standard Baseline Parameters"
    rec = "Immediate cardiologist referral advised. Schedule ECG, echocardiogram, and lipid fraction panel." if res == 1 else "Maintain regular aerobic exercises, balanced sodium intake, and perform routine annual cardiac checkups."
    
    return create_interactive_result_card("Heart Assessment", result_text, "High Risk" if res == 1 else "Optimal", 88 if res == 1 else 12, rec, biomarkers, risk_level, is_risk=(res == 1))

def predict_diabetes(username, gender, age, hypertension, heart_disease, smoking, bmi, hba1c, glucose):
    gender_map = {"Female": 0, "Male": 1, "Other": 2}
    smoke_map = {"Never": 0, "No Info": 1, "Current": 2, "Former": 3, "Ever": 4, "Not Current": 5}
    data = np.array([[gender_map[gender], float(age), float(hypertension), float(heart_disease),
                      smoke_map[smoking], float(bmi), float(hba1c), float(glucose)]])
    res = diabetes_model.predict(data)[0]
    result_text = "Elevated Diabetes Risk" if res == 1 else "Normal Glycemic Baseline"
    save_user_record(username, "Diabetes Analysis", result_text)
    
    biomarkers = f"HbA1c: {hba1c}% | Fasting Glucose: {glucose} mg/dL | BMI: {bmi} kg/m² | Hypertension Status: {hypertension}"
    risk_level = "Hyperglycemia / Diabetes Type II Biomarkers Present" if res == 1 else "Normoglycemic Baseline"
    rec = "Consult an endocrinologist for an Oral Glucose Tolerance Test (OGTT) and personalized dietary intervention." if res == 1 else "Maintain a low-glycemic-index diet, active daily routine, and annual glucose monitoring."
    
    return create_interactive_result_card("Diabetes Assessment", result_text, "Action Required" if res == 1 else "In-Range", 92 if res == 1 else 15, rec, biomarkers, risk_level, is_risk=(res == 1))

def predict_kidney(username, age, gender, bp, creatinine, urea, hb, rbc, hypertension, egfr, albumin):
    data = np.array([[float(age), 1 if gender == "Male" else 0, float(bp), float(creatinine),
                      float(urea), float(hb), float(rbc), 1 if hypertension == "Yes" else 0,
                      float(egfr), 1 if albumin == "Yes" else 0]])
    res = kidney_model.predict(data)[0]
    result_text = "Renal Dysfunction Indicator" if res == 1 else "Healthy Kidney Parameters"
    save_user_record(username, "Kidney Function", result_text)
    
    biomarkers = f"eGFR: {egfr} mL/min | Serum Creatinine: {creatinine} mg/dL | Blood Urea: {urea} mg/dL | Albuminuria: {albumin}"
    risk_level = "Elevated Risk of Chronic Kidney Impairment" if res == 1 else "Optimal Glomerular Filtration Rate"
    rec = "Nephrology evaluation recommended. Order urinalysis, microalbumin test, and monitor fluid balance." if res == 1 else "Ensure adequate daily hydration (2-3L water) and limit unnecessary NSAID medication usage."
    
    return create_interactive_result_card("Kidney Panel", result_text, "High Risk" if res == 1 else "Optimal", 84 if res == 1 else 10, rec, biomarkers, risk_level, is_risk=(res == 1))

def predict_liver(username, age, gender, tb, db, alk, sgpt, sgot, proteins, albumin, ratio):
    data = np.array([[float(age), 1 if gender == "Male" else 0, float(tb), float(db),
                      float(alk), float(sgpt), float(sgot), float(proteins), float(albumin), float(ratio)]])
    res = liver_model.predict(data)[0]
    result_text = "Hepatic Enzyme Anomaly" if res == 1 else "Normal Liver Panel"
    save_user_record(username, "Liver Function", result_text)
    
    biomarkers = f"Total Bilirubin: {tb} | Direct Bilirubin: {db} | SGPT/ALT: {sgpt} U/L | SGOT/AST: {sgot} U/L | A/G Ratio: {ratio}"
    risk_level = "Elevated Transaminases / Hepatic Stress" if res == 1 else "Balanced Hepatic Biomarkers"
    rec = "Schedule an abdominal ultrasound and evaluate liver enzyme trends with a gastroenterologist." if res == 1 else "Limit alcohol consumption, maintain a clean diet, and recheck liver panel annually."
    
    return create_interactive_result_card("Liver Function", result_text, "Elevated Risk" if res == 1 else "In-Range", 78 if res == 1 else 14, rec, biomarkers, risk_level, is_risk=(res == 1))

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
    bmi_calc = round(float(weight) / (float(height) ** 2), 2)
    biomarkers = f"Calculated BMI: {bmi_calc} kg/m² | Height: {height}m | Weight: {weight}kg | Physical Activity Frequency: {faf}/3"
    risk_level = f"Classified Category: {lbl}"
    rec = "Consult with a registered dietitian for tailored caloric management and resistance training recommendations." if is_risk else "Maintain active lifestyle and current caloric balance."
    
    return create_interactive_result_card("Body Mass Index", lbl, "Attention" if is_risk else "Optimal", pct, rec, biomarkers, risk_level, is_risk=is_risk)

# --- NAVIGATION HANDLERS ---
def handle_user_login(username, password):
    if verify_user(username, password):
        user_hist = get_user_history(username)
        t, h, d, k, l = get_dashboard_counts(username)
        welcome_html = f"""
        <div style="background: linear-gradient(135deg, #4F46E5 0%, #312E81 100%); border-radius: 20px; padding: 24px; color: #FFFFFF; display: flex; align-items: center; justify-content: space-between; border: 1px solid #6366F1; box-shadow: 0 10px 25px rgba(0,0,0,0.4);">
            <div>
                <div style="background: rgba(255,255,255,0.15); display: inline-block; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.8rem; margin-bottom: 8px; color: #E0E7FF;">CLINICAL PORTAL ACTIVE</div>
                <h2 style="margin: 0; font-size: 1.9rem; font-weight: 900; color: #FFFFFF; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">Welcome, Dr. {username}</h2>
                <p style="margin: 6px 0 0 0; color: #E0E7FF; font-size: 1rem; font-weight: 500;">Ready for diagnostic triage and automated machine learning evaluation.</p>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 14px 22px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.2); text-align: right;">
                <div style="font-size: 0.8rem; color: #94A3B8; font-weight: 700;">SYSTEM DATE</div>
                <div style="font-size: 1.1rem; font-weight: 800; color: #38BDF8;">📅 {datetime.now().strftime('%b %d, %Y')}</div>
            </div>
        </div>
        """
        metrics_html = f"""
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-top: 18px;">
            <div style="background: #1B1E32; border-radius: 16px; padding: 16px; text-align: center; border: 1px solid #2D3256;">
                <div style="font-size: 1.8rem; margin-bottom: 4px;">📊</div>
                <div style="color: #9CA3AF; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Total Diagnostics</div>
                <div style="color: #FFFFFF; font-size: 1.6rem; font-weight: 900; margin-top: 2px;">{t}</div>
            </div>
            <div style="background: #1B1E32; border-radius: 16px; padding: 16px; text-align: center; border: 1px solid #2D3256;">
                <div style="font-size: 1.8rem; margin-bottom: 4px;">❤️</div>
                <div style="color: #9CA3AF; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Heart Records</div>
                <div style="color: #FFFFFF; font-size: 1.6rem; font-weight: 900; margin-top: 2px;">{h}</div>
            </div>
            <div style="background: #1B1E32; border-radius: 16px; padding: 16px; text-align: center; border: 1px solid #2D3256;">
                <div style="font-size: 1.8rem; margin-bottom: 4px;">🩸</div>
                <div style="color: #9CA3AF; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Diabetes Tests</div>
                <div style="color: #FFFFFF; font-size: 1.6rem; font-weight: 900; margin-top: 2px;">{d}</div>
            </div>
            <div style="background: #1B1E32; border-radius: 16px; padding: 16px; text-align: center; border: 1px solid #2D3256;">
                <div style="font-size: 1.8rem; margin-bottom: 4px;">🫘</div>
                <div style="color: #9CA3AF; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Kidney Panels</div>
                <div style="color: #FFFFFF; font-size: 1.6rem; font-weight: 900; margin-top: 2px;">{k}</div>
            </div>
            <div style="background: #1B1E32; border-radius: 16px; padding: 16px; text-align: center; border: 1px solid #2D3256;">
                <div style="font-size: 1.8rem; margin-bottom: 4px;">🫀</div>
                <div style="color: #9CA3AF; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Liver Panels</div>
                <div style="color: #FFFFFF; font-size: 1.6rem; font-weight: 900; margin-top: 2px;">{l}</div>
            </div>
        </div>
        """
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), "", username, user_hist, welcome_html, metrics_html
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "❌ <span style='color: #FF5A5A; font-weight: bold;'>Invalid credentials. Please verify your login details.</span>", "", [], "", ""

def handle_admin_login(passcode):
    if passcode == ADMIN_SECRET_KEY:
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), "", "", [], "", "", get_all_users()
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "❌ <span style='color: #FF5A5A; font-weight: bold;'>Incorrect Admin Key.</span>", "", [], "", "", []

def handle_logout():
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "", "", [], "", ""

# --- HIGH-CONTRAST DARK CSS (FIXES ALL TEXT VISIBILITY ISSUES) ---
css = """
/* BASE THEME COLORS */
:root {
    --bg-main: #0B0D17;
    --card-bg: #151828;
    --accent-blue: #6366F1;
    --accent-hover: #4F46E5;
    --text-bright: #FFFFFF;
    --text-muted: #D1D5DB;
    --border-color: #2D3256;
}

body, .gradio-container {
    background-color: var(--bg-main) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: var(--text-bright) !important;
}

/* CARDS & PANELS */
.dark-dashboard-card {
    background: var(--card-bg) !important;
    border-radius: 20px !important;
    padding: 24px !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5) !important;
}

/* SCROLL PANEL */
.scroll-panel {
    max-height: 540px;
    overflow-y: auto !important;
    padding-right: 10px;
}
.scroll-panel::-webkit-scrollbar { width: 8px; }
.scroll-panel::-webkit-scrollbar-track { background: #121422; border-radius: 10px; }
.scroll-panel::-webkit-scrollbar-thumb { background: #374151; border-radius: 10px; }

/* FIX TAB TEXT VISIBILITY */
button[role="tab"] {
    color: #9CA3AF !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    background: #111322 !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    padding: 10px 20px !important;
    margin-right: 6px !important;
    transition: all 0.2s ease !important;
}

button[role="tab"]:hover {
    color: #FFFFFF !important;
    background: #1F233A !important;
}

button[role="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    background: var(--accent-blue) !important;
    border-color: #818CF8 !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
}

/* FIX INPUT LABELS & TEXT FIELDS */
label span { 
    color: #F3F4F6 !important; 
    font-weight: 700 !important; 
    font-size: 0.9rem !important; 
    margin-bottom: 4px !important;
}

input, select, textarea, .ts-control {
    background-color: #0F111E !important;
    color: #FFFFFF !important;
    border: 1px solid #373E68 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
}

input:focus, select:focus, textarea:focus {
    border-color: #818CF8 !important;
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.2) !important;
}

/* NUMERIC & DROPDOWN TEXT IN LIGHT MODES (OVERRIDE GRADIO INTERNAL DARKNESS) */
.gradio-dropdown input, .gradio-number input {
    color: #FFFFFF !important;
}

/* PRIMARY ACTION BUTTONS */
button.primary-btn {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
    color: #FFFFFF !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    padding: 14px !important;
    border: none !important;
    box-shadow: 0 6px 18px rgba(99, 102, 241, 0.35) !important;
    cursor: pointer !important;
    margin-top: 14px !important;
    transition: transform 0.1s ease, box-shadow 0.2s ease !important;
}

button.primary-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 22px rgba(99, 102, 241, 0.5) !important;
}

/* LOGOUT BUTTON */
button.logout-btn {
    background: #2A1724 !important;
    color: #FF6B81 !important;
    border: 1px solid #FF3B5C !important;
    font-weight: 800 !important;
    border-radius: 12px !important;
    transition: background 0.2s ease !important;
}

button.logout-btn:hover {
    background: #3D1C30 !important;
}

/* DATAFRAME TEXT VISIBILITY */
.dataframe th {
    background-color: #1E2238 !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
}

.dataframe td {
    background-color: #0F111E !important;
    color: #E5E7EB !important;
    font-weight: 600 !important;
}

footer { visibility: hidden !important; }
"""

with gr.Blocks(css=css, title="Sick Sense Clinical Dashboard") as demo:
    current_user_state = gr.State(value="")

    # ------------------ ENHANCED INFORMATIONAL AUTHENTICATION PORTAL ------------------
    with gr.Column(visible=True, elem_classes=["dark-dashboard-card"]) as auth_view:
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("""
                # 🏥 **Sick Sense Clinical AI**
                ### *Next-Generation Machine Learning Health Diagnostics*
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div style="background: #111322; border-left: 4px solid #6366F1; padding: 12px 16px; border-radius: 8px;">
                    <span style="color: #22C55E; font-weight: 800; font-size: 0.85rem;">● SYSTEM ONLINE</span><br/>
                    <span style="color: #D1D5DB; font-size: 0.85rem; font-weight: 600;">5 Machine Learning Models Loaded (Heart, Diabetes, Kidney, Liver, BMI)</span>
                </div>
                """)

        gr.Markdown("---")

        with gr.Row():
            # LEFT: LOGIN & REGISTRATION FORM
            with gr.Column(scale=1.2):
                with gr.Tabs():
                    with gr.Tab("🔑 Sign In"):
                        username_input = gr.Textbox(label="Username", placeholder="Enter your medical license / username")
                        password_input = gr.Textbox(label="Password", type="password", placeholder="Enter secure password")
                        login_btn = gr.Button("Sign In to Workstation", elem_classes=["primary-btn"])
                        login_msg = gr.HTML("")

                    with gr.Tab("📝 Create Account"):
                        new_username = gr.Textbox(label="New Username", placeholder="Choose account username")
                        new_password = gr.Textbox(label="New Password", type="password", placeholder="Choose password")
                        confirm_password = gr.Textbox(label="Confirm Password", type="password", placeholder="Re-enter password")
                        signup_btn = gr.Button("Register New Account", elem_classes=["primary-btn"])
                        signup_msg = gr.HTML("")

                    with gr.Tab("🛡️ Admin Portal"):
                        admin_key_input = gr.Textbox(label="Admin Key", type="password", placeholder="Enter administrative key")
                        admin_login_btn = gr.Button("Access Admin Management Panel", elem_classes=["primary-btn"])
                        admin_msg = gr.HTML("")

            # RIGHT: CLINICAL SYSTEM INFORMATION CARDS
            with gr.Column(scale=1):
                gr.HTML("""
                <div style="background: #111322; border: 1px solid #2D3256; border-radius: 16px; padding: 20px;">
                    <h3 style="color: #FFFFFF; margin-top:0; font-size: 1.1rem; font-weight: 800;">💡 System Capability Brief</h3>
                    <ul style="color: #D1D5DB; font-size: 0.88rem; line-height: 1.7; padding-left: 20px; margin-bottom: 0;">
                        <li><strong style="color: #818CF8;">Cardiovascular Risk:</strong> Evaluates 13 heart biomarkers including ST depression and resting blood pressure.</li>
                        <li><strong style="color: #818CF8;">Glycemic Analysis:</strong> Assesses HbA1c, fasting glucose levels, and BMI indexes.</li>
                        <li><strong style="color: #818CF8;">Renal & Hepatic Panels:</strong> Measures serum creatinine, eGFR, direct bilirubin, and transaminase balances.</li>
                        <li><strong style="color: #818CF8;">Automated Tracking:</strong> Saves every diagnostic result into an encrypted persistent medical database.</li>
                    </ul>
                </div>
                """)

    # ------------------ MAIN CLINICAL DASHBOARD ------------------
    with gr.Row(visible=False, elem_classes=["dark-dashboard-card"]) as user_dashboard_view:
        # LEFT NAVIGATION SIDEBAR
        with gr.Column(scale=1, min_width=200):
            gr.HTML("""
            <div style="text-align: center; padding-bottom: 12px;">
                <div style="font-size: 2.2rem;">🏥</div>
                <div style="font-weight: 900; color: #FFFFFF; font-size: 1.2rem; margin-top: 4px;">Sick Sense</div>
                <div style="color: #818CF8; font-size: 0.75rem; font-weight: 700;">CLINICAL WORKSTATION</div>
            </div>
            """)
            gr.Markdown("---")
            gr.HTML("""
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <div style="background: #252945; color: #FFFFFF; padding: 10px 14px; border-radius: 10px; font-weight: 700; font-size: 0.9rem; border-left: 4px solid #6366F1;">
                    🏠 Workstation Dashboard
                </div>
                <div style="color: #9CA3AF; padding: 10px 14px; font-weight: 600; font-size: 0.9rem;">
                    📅 Patient Appointments
                </div>
                <div style="color: #9CA3AF; padding: 10px 14px; font-weight: 600; font-size: 0.9rem;">
                    📊 Analytics & Reports
                </div>
                <div style="color: #9CA3AF; padding: 10px 14px; font-weight: 600; font-size: 0.9rem;">
                    ⚙️ Workstation Settings
                </div>
            </div>
            """)
            gr.Markdown("---")
            user_logout_btn = gr.Button("🚪 Sign Out", elem_classes=["logout-btn"])

        # MAIN CONTENT AREA
        with gr.Column(scale=5):
            welcome_banner = gr.HTML()
            metrics_banner = gr.HTML()
            
            gr.Markdown("---")

            with gr.Tabs():
                # Heart Health Tab
                with gr.Tab("❤️ Heart Diagnostic"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        gr.Markdown("#### Enter Patient Cardiovascular Parameters")
                        with gr.Row():
                            age = gr.Number(label="Age (Years)", value=45)
                            sex = gr.Dropdown(["0", "1"], value="1", label="Biological Sex (1=Male, 0=Female)")
                            cp = gr.Dropdown(["0", "1", "2", "3"], value="0", label="Chest Pain Type (0-3)")
                        with gr.Row():
                            trestbps = gr.Number(label="Resting BP (mm Hg)", value=130)
                            chol = gr.Number(label="Serum Cholesterol (mg/dl)", value=250)
                            fbs = gr.Dropdown(["0", "1"], value="0", label="Fasting Blood Sugar > 120 mg/dl (1=True, 0=False)")
                        with gr.Row():
                            restecg = gr.Dropdown(["0", "1", "2"], value="1", label="Resting ECG Results (0-2)")
                            thalach = gr.Number(label="Max Heart Rate Achieved", value=150)
                            exang = gr.Dropdown(["0", "1"], value="0", label="Exercise Induced Angina (1=Yes, 0=No)")
                        with gr.Row():
                            oldpeak = gr.Number(label="ST Depression Induced by Exercise", value=1.2)
                            slope = gr.Dropdown(["0", "1", "2"], value="2", label="Slope of Peak Exercise ST Segment")
                            ca = gr.Dropdown(["0", "1", "2", "3", "4"], value="0", label="Number of Major Vessels Colored by Fluoroscopy")
                            thal = gr.Dropdown(["0", "1", "2", "3"], value="2", label="Thalassemia Score (1=Normal, 2=Fixed, 3=Reversible)")

                        heart_btn = gr.Button("⚡ Run Cardiac Risk Evaluation", elem_classes=["primary-btn"])
                        heart_output = gr.HTML()

                # Diabetes Tab
                with gr.Tab("🩸 Diabetes Diagnostic"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        gr.Markdown("#### Enter Patient Glycemic Parameters")
                        with gr.Row():
                            gender = gr.Dropdown(["Female", "Male", "Other"], value="Male", label="Gender")
                            d_age = gr.Number(label="Age (Years)", value=40)
                        with gr.Row():
                            hypertension = gr.Dropdown([0, 1], value=0, label="Hypertension History (0=No, 1=Yes)")
                            heart_disease = gr.Dropdown([0, 1], value=0, label="Heart Disease History (0=No, 1=Yes)")
                        smoking = gr.Dropdown(["Never", "No Info", "Current", "Former", "Ever", "Not Current"], value="Never", label="Smoking History Profile")
                        with gr.Row():
                            bmi = gr.Number(label="Body Mass Index (BMI)", value=24.5)
                            hba1c = gr.Number(label="HbA1c Level (%)", value=5.6)
                            glucose = gr.Number(label="Fasting Blood Glucose (mg/dL)", value=110)

                        diabetes_btn = gr.Button("⚡ Analyze Glycemic & Metabolic Profile", elem_classes=["primary-btn"])
                        diabetes_output = gr.HTML()

                # Kidney Tab
                with gr.Tab("🫘 Kidney Function"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        gr.Markdown("#### Enter Patient Renal Parameters")
                        with gr.Row():
                            k_age = gr.Number(label="Age (Years)", value=48)
                            k_gender = gr.Dropdown(["Male", "Female"], value="Male", label="Gender")
                            k_bp = gr.Number(label="Blood Pressure (mm Hg)", value=80)
                        with gr.Row():
                            k_creatinine = gr.Number(label="Serum Creatinine (mg/dL)", value=1.2)
                            k_urea = gr.Number(label="Blood Urea (mg/dL)", value=36)
                            k_hb = gr.Number(label="Hemoglobin Level (g/dL)", value=15.4)
                        with gr.Row():
                            k_rbc = gr.Number(label="Red Blood Cell Count", value=5.2)
                            k_hypertension = gr.Dropdown(["No", "Yes"], value="No", label="Hypertension Diagnosis")
                            k_egfr = gr.Number(label="eGFR Rate", value=90)
                            k_albumin = gr.Dropdown(["No", "Yes"], value="No", label="Albumin Presence in Urine")

                        kidney_btn = gr.Button("⚡ Run Renal Function Assessment", elem_classes=["primary-btn"])
                        kidney_output = gr.HTML()

                # Liver Tab
                with gr.Tab("🫀 Liver Function"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        gr.Markdown("#### Enter Patient Hepatic Parameters")
                        with gr.Row():
                            l_age = gr.Number(label="Age (Years)", value=55)
                            l_gender = gr.Dropdown(["Male", "Female"], value="Male", label="Gender")
                            l_tb = gr.Number(label="Total Bilirubin (mg/dL)", value=0.8)
                        with gr.Row():
                            l_db = gr.Number(label="Direct Bilirubin (mg/dL)", value=0.2)
                            l_alk = gr.Number(label="Alkaline Phosphatase (U/L)", value=180)
                            l_sgpt = gr.Number(label="SGPT / ALT Level (U/L)", value=22)
                        with gr.Row():
                            l_sgot = gr.Number(label="SGOT / AST Level (U/L)", value=24)
                            l_proteins = gr.Number(label="Total Proteins (g/dL)", value=6.8)
                            l_albumin = gr.Number(label="Albumin Level (g/dL)", value=3.5)
                            l_ratio = gr.Number(label="Albumin / Globulin Ratio", value=1.0)

                        liver_btn = gr.Button("⚡ Analyze Hepatic Biomarker Panel", elem_classes=["primary-btn"])
                        liver_output = gr.HTML()

                # Body Mass Tab
                with gr.Tab("⚖️ Mass & Lifestyle"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        gr.Markdown("#### Enter Patient Anthropometric Data")
                        with gr.Row():
                            o_gender = gr.Dropdown(["Female", "Male"], value="Male", label="Gender")
                            o_age = gr.Number(label="Age (Years)", value=22)
                            o_height = gr.Number(label="Height (Meters)", value=1.75)
                            o_weight = gr.Number(label="Weight (Kilograms)", value=70)
                        with gr.Row():
                            o_family = gr.Dropdown(["No", "Yes"], value="Yes", label="Family Overweight History")
                            o_favc = gr.Dropdown(["No", "Yes"], value="Yes", label="Frequent High Caloric Food")
                            o_fcvc = gr.Number(label="Vegetable Intake Frequency (1-3)", value=2)
                            o_ncp = gr.Number(label="Number of Main Meals (1-4)", value=3)
                        with gr.Row():
                            o_caec = gr.Dropdown(["No", "Sometimes", "Frequently", "Always"], value="Sometimes", label="Snack Consumption Frequency")
                            o_smoke = gr.Dropdown(["No", "Yes"], value="No", label="Smoker")
                            o_ch2o = gr.Number(label="Daily Water Intake (1-3)", value=2)
                            o_scc = gr.Dropdown(["No", "Yes"], value="No", label="Calorie Intake Monitoring")
                        with gr.Row():
                            o_faf = gr.Number(label="Physical Activity Frequency (0-3)", value=1)
                            o_tue = gr.Number(label="Screen Device Time (0-2)", value=1)
                            o_calc = gr.Dropdown(["No", "Sometimes", "Frequently", "Always"], value="Sometimes", label="Alcohol Consumption")
                            o_mtrans = gr.Dropdown(["Public Transportation", "Walking", "Automobile", "Motorbike", "Bike"], value="Public Transportation", label="Primary Transportation Mode")

                        obesity_btn = gr.Button("⚡ Analyze Body Mass Profile", elem_classes=["primary-btn"])
                        obesity_output = gr.HTML()

                # History Tab
                with gr.Tab("📜 Medical History Log"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        gr.Markdown("#### Patient Examination Log History")
                        history_table = gr.Dataframe(headers=["Test Module", "Outcome Result", "Date & Time"], value=[], interactive=False)
                        refresh_history_btn = gr.Button("🔄 Refresh Saved Records", elem_classes=["primary-btn"])

    # ------------------ ADMIN PANEL PAGE ------------------
    with gr.Column(visible=False, elem_classes=["dark-dashboard-card"]) as admin_dashboard_view:
        with gr.Row():
            gr.Markdown("### 🛡️ Administrative Database Management")
            admin_logout_btn = gr.Button("Exit Panel", elem_classes=["logout-btn"], scale=0, min_width=120)

        with gr.Column(elem_classes=["scroll-panel"]):
            user_table = gr.Dataframe(headers=["User ID", "Registered Username"], value=[], interactive=False)
            refresh_btn = gr.Button("🔄 Refresh Database Table", elem_classes=["primary-btn"])

            gr.Markdown("---")
            gr.Markdown("#### Remove User Account")
            with gr.Row():
                user_to_delete = gr.Textbox(label="Target Username", placeholder="Enter exact username")
                delete_user_btn = gr.Button("Delete Account & Logs", elem_classes=["primary-btn"])
            admin_action_msg = gr.HTML("")

    # ------------------ EVENT LISTENERS ------------------
    signup_btn.click(register_user, inputs=[new_username, new_password, confirm_password], outputs=[signup_msg])
    login_btn.click(handle_user_login, inputs=[username_input, password_input], outputs=[auth_view, user_dashboard_view, admin_dashboard_view, login_msg, current_user_state, history_table, welcome_banner, metrics_banner])
    admin_login_btn.click(handle_admin_login, inputs=[admin_key_input], outputs=[auth_view, user_dashboard_view, admin_dashboard_view, admin_msg, current_user_state, history_table, welcome_banner, metrics_banner, user_table])
    
    user_logout_btn.click(handle_logout, inputs=[], outputs=[auth_view, user_dashboard_view, admin_dashboard_view, username_input, password_input, history_table, current_user_state])
    admin_logout_btn.click(handle_logout, inputs=[], outputs=[auth_view, user_dashboard_view, admin_dashboard_view, admin_key_input, admin_msg, history_table, current_user_state])
    
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
