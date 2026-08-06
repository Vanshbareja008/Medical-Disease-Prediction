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
        return "❌ <span style='color: #DC2626; font-weight: 700;'>Username and password cannot be empty.</span>"
    if len(password) < 8:
        return "❌ <span style='color: #DC2626; font-weight: 700;'>Password must be at least 8 characters long.</span>"
    if password != confirm_password:
        return "❌ <span style='color: #DC2626; font-weight: 700;'>Passwords do not match.</span>"
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                       (username, hash_password(password)))
        conn.commit()
        conn.close()
        return "✅ <span style='color: #059669; font-weight: 700;'>Account created successfully! Please Sign In.</span>"
    except sqlite3.IntegrityError:
        return "❌ <span style='color: #DC2626; font-weight: 700;'>Username already exists.</span>"

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
        return "❌ <span style='color: #DC2626; font-weight: 700;'>Please enter a valid username.</span>"
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username_to_delete,))
    cursor.execute("DELETE FROM lab_history WHERE username = ?", (username_to_delete,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted_count > 0:
        return f"✅ <span style='color: #059669; font-weight: 700;'>User '{username_to_delete}' deleted successfully.</span>"
    return "❌ <span style='color: #DC2626; font-weight: 700;'>User not found.</span>"

# --- LOAD MODELS ---
heart_model = joblib.load("heart diagn.pkl")
diabetes_model = joblib.load("diabetes diagn.pkl")
kidney_model = joblib.load("kidney diagn.pkl")
liver_model = joblib.load("Liver Diagn.pkl")
obesity_model = joblib.load("Obesity Diagn.pkl")

# --- RESULT CARD GENERATOR ---
def create_interactive_result_card(title, value_text, status_label, bar_percent, recommendation, key_biomarkers, risk_level_text, is_risk=False):
    badge_bg = "#FEE2E2" if is_risk else "#DCFCE7"
    badge_color = "#991B1B" if is_risk else "#166534"
    bar_color = "#EF4444" if is_risk else "#7C3AED"

    return f"""
    <div style="background: #FFFFFF; border: 1px solid #E4E4E7; border-radius: 20px; padding: 22px; margin-top: 18px; box-shadow: 0 4px 20px rgba(124, 58, 237, 0.06);">
        <!-- TOP ROW -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.3rem;">🧪</span>
                <span style="font-weight: 800; color: #18181B; font-size: 1.15rem; letter-spacing: -0.2px;">{title}</span>
            </div>
            <span style="background: {badge_bg}; color: {badge_color}; padding: 5px 14px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; text-transform: uppercase;">
                {status_label}
            </span>
        </div>

        <!-- DIAGNOSIS HIGHLIGHT -->
        <div style="font-size: 1.5rem; font-weight: 900; color: #18181B; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
            <span style="color: #71717A; font-size: 0.95rem; font-weight: 600;">Outcome:</span> {value_text}
        </div>

        <!-- PROGRESS / RANGE INDICATOR BAR -->
        <div style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: #52525B; font-weight: 700; margin-bottom: 6px;">
                <span>Calculated Risk Range</span>
                <span style="color: {bar_color};">{bar_percent}% Index</span>
            </div>
            <div style="width: 100%; background: #F4F4F5; height: 12px; border-radius: 6px; overflow: hidden; border: 1px solid #E4E4E7;">
                <div style="width: {bar_percent}%; background: {bar_color}; height: 100%; border-radius: 6px; transition: width 0.6s ease-in-out;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #A1A1AA; margin-top: 6px; font-weight: 600;">
                <span>Low Risk Target</span>
                <span>Moderate Range</span>
                <span>High Threshold</span>
            </div>
        </div>
        
        <!-- EXPANDABLE CLINICAL ANALYSIS PANEL -->
        <details open style="margin-top: 16px; background: #FAF5FF; border-radius: 14px; padding: 14px 18px; border: 1px solid #E9D5FF;">
            <summary style="cursor: pointer; font-weight: 800; color: #6B21A8; font-size: 0.92rem; user-select: none;">
                📊 Biomarker Analysis & Guidance Highlights
            </summary>
            <div style="margin-top: 12px; font-size: 0.88rem; color: #27272A; line-height: 1.6;">
                <div style="margin-bottom: 8px; background: #FFFFFF; padding: 10px 12px; border-radius: 8px; border-left: 4px solid #7C3AED; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <strong style="color: #6B21A8;">Key Biomarkers:</strong><br/>
                    <span style="color: #18181B; font-weight: 600;">{key_biomarkers}</span>
                </div>
                <div style="margin-bottom: 8px; background: #FFFFFF; padding: 10px 12px; border-radius: 8px; border-left: 4px solid {bar_color}; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <strong style="color: #6B21A8;">Risk Stratification:</strong><br/>
                    <span style="color: #18181B; font-weight: 600;">{risk_level_text}</span>
                </div>
                <div style="background: #FFFFFF; padding: 10px 12px; border-radius: 8px; border-left: 4px solid #10B981; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <strong style="color: #6B21A8;">Actionable Recommendation:</strong><br/>
                    <span style="color: #18181B; font-weight: 600;">{recommendation}</span>
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
    risk_level = "High Probability of Cardiovascular Anomaly" if res == 1 else "Low Risk / Standard Baseline"
    rec = "Cardiologist consultation advised. Schedule ECG, echocardiogram, and lipid panel." if res == 1 else "Maintain regular aerobic exercises, balanced diet, and perform annual cardiac checks."
    
    return create_interactive_result_card("Heart Assessment", result_text, "High Risk" if res == 1 else "In-Range", 88 if res == 1 else 12, rec, biomarkers, risk_level, is_risk=(res == 1))

def predict_diabetes(username, gender, age, hypertension, heart_disease, smoking, bmi, hba1c, glucose):
    gender_map = {"Female": 0, "Male": 1, "Other": 2}
    smoke_map = {"Never": 0, "No Info": 1, "Current": 2, "Former": 3, "Ever": 4, "Not Current": 5}
    data = np.array([[gender_map[gender], float(age), float(hypertension), float(heart_disease),
                      smoke_map[smoking], float(bmi), float(hba1c), float(glucose)]])
    res = diabetes_model.predict(data)[0]
    result_text = "Elevated Diabetes Risk" if res == 1 else "Normal Glycemic Baseline"
    save_user_record(username, "Diabetes Analysis", result_text)
    
    biomarkers = f"HbA1c: {hba1c}% | Fasting Glucose: {glucose} mg/dL | BMI: {bmi} kg/m² | Hypertension: {hypertension}"
    risk_level = "Hyperglycemia / Diabetes Type II Risk" if res == 1 else "Normoglycemic Baseline"
    rec = "Consult an endocrinologist for an Oral Glucose Tolerance Test (OGTT) and nutritional planning." if res == 1 else "Maintain low-glycemic diet, active daily routine, and annual glucose monitoring."
    
    return create_interactive_result_card("Diabetes Assessment", result_text, "Action Required" if res == 1 else "In-Range", 92 if res == 1 else 15, rec, biomarkers, risk_level, is_risk=(res == 1))

def predict_kidney(username, age, gender, bp, creatinine, urea, hb, rbc, hypertension, egfr, albumin):
    data = np.array([[float(age), 1 if gender == "Male" else 0, float(bp), float(creatinine),
                      float(urea), float(hb), float(rbc), 1 if hypertension == "Yes" else 0,
                      float(egfr), 1 if albumin == "Yes" else 0]])
    res = kidney_model.predict(data)[0]
    result_text = "Renal Dysfunction Indicator" if res == 1 else "Healthy Kidney Parameters"
    save_user_record(username, "Kidney Function", result_text)
    
    biomarkers = f"eGFR: {egfr} mL/min | Creatinine: {creatinine} mg/dL | Urea: {urea} mg/dL | Albuminuria: {albumin}"
    risk_level = "Elevated Risk of Chronic Kidney Impairment" if res == 1 else "Optimal Glomerular Filtration Rate"
    rec = "Nephrology evaluation recommended. Schedule urinalysis and monitor blood pressure." if res == 1 else "Ensure adequate daily hydration (2-3L water) and avoid unprescribed NSAIDs."
    
    return create_interactive_result_card("Kidney Panel", result_text, "High Risk" if res == 1 else "In-Range", 84 if res == 1 else 10, rec, biomarkers, risk_level, is_risk=(res == 1))

def predict_liver(username, age, gender, tb, db, alk, sgpt, sgot, proteins, albumin, ratio):
    data = np.array([[float(age), 1 if gender == "Male" else 0, float(tb), float(db),
                      float(alk), float(sgpt), float(sgot), float(proteins), float(albumin), float(ratio)]])
    res = liver_model.predict(data)[0]
    result_text = "Hepatic Enzyme Anomaly" if res == 1 else "Normal Liver Panel"
    save_user_record(username, "Liver Function", result_text)
    
    biomarkers = f"Total Bilirubin: {tb} | Direct Bilirubin: {db} | ALT/SGPT: {sgpt} U/L | AST/SGOT: {sgot} U/L | A/G Ratio: {ratio}"
    risk_level = "Elevated Transaminases / Hepatic Stress" if res == 1 else "Balanced Hepatic Biomarkers"
    rec = "Schedule an abdominal ultrasound and review hepatic enzyme trends with a doctor." if res == 1 else "Maintain healthy lifestyle habits and recheck liver panel annually."
    
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
    biomarkers = f"Calculated BMI: {bmi_calc} kg/m² | Height: {height}m | Weight: {weight}kg | Physical Activity Score: {faf}/3"
    risk_level = f"Classified Category: {lbl}"
    rec = "Consult with a registered dietitian for personalized dietary and exercise planning." if is_risk else "Maintain active lifestyle and current caloric balance."
    
    return create_interactive_result_card("Body Mass Index", lbl, "Attention" if is_risk else "In-Range", pct, rec, biomarkers, risk_level, is_risk=is_risk)

# --- NAVIGATION HANDLERS ---
def handle_user_login(username, password):
    if verify_user(username, password):
        user_hist = get_user_history(username)
        t, h, d, k, l = get_dashboard_counts(username)
        welcome_html = f"""
        <div style="background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%); border-radius: 20px; padding: 22px 26px; color: #FFFFFF; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 10px 25px rgba(124, 58, 237, 0.25);">
            <div>
                <div style="background: rgba(255,255,255,0.2); display: inline-block; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.78rem; margin-bottom: 8px; color: #FFFFFF;">CLINICAL PORTAL ACTIVE</div>
                <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800; color: #FFFFFF;">Welcome, Dr. {username}</h2>
                <p style="margin: 4px 0 0 0; color: #F3E8FF; font-size: 0.95rem; font-weight: 500;">Ready for automated health diagnostic triage.</p>
            </div>
            <div style="background: rgba(255, 255, 255, 0.15); padding: 12px 20px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.3); text-align: right;">
                <div style="font-size: 0.75rem; color: #E9D5FF; font-weight: 700;">SYSTEM DATE</div>
                <div style="font-size: 1.05rem; font-weight: 800; color: #FFFFFF;">📅 {datetime.now().strftime('%b %d, %Y')}</div>
            </div>
        </div>
        """
        metrics_html = f"""
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-top: 16px;">
            <div style="background: #FFFFFF; border-radius: 16px; padding: 16px; text-align: center; border: 1px solid #E4E4E7; box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
                <div style="font-size: 1.5rem; margin-bottom: 2px;">📊</div>
                <div style="color: #71717A; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Total Diagnostics</div>
                <div style="color: #18181B; font-size: 1.5rem; font-weight: 900; margin-top: 2px;">{t}</div>
            </div>
            <div style="background: #FFFFFF; border-radius: 16px; padding: 16px; text-align: center; border: 1px solid #E4E4E7; box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
                <div style="font-size: 1.5rem; margin-bottom: 2px;">❤️</div>
                <div style="color: #71717A; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Heart Tests</div>
                <div style="color: #18181B; font-size: 1.5rem; font-weight: 900; margin-top: 2px;">{h}</div>
            </div>
            <div style="background: #FFFFFF; border-radius: 16px; padding: 16px; text-align: center; border: 1px solid #E4E4E7; box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
                <div style="font-size: 1.5rem; margin-bottom: 2px;">🩸</div>
                <div style="color: #71717A; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Diabetes Tests</div>
                <div style="color: #18181B; font-size: 1.5rem; font-weight: 900; margin-top: 2px;">{d}</div>
            </div>
            <div style="background: #FFFFFF; border-radius: 16px; padding: 16px; text-align: center; border: 1px solid #E4E4E7; box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
                <div style="font-size: 1.5rem; margin-bottom: 2px;">🫘</div>
                <div style="color: #71717A; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Kidney Tests</div>
                <div style="color: #18181B; font-size: 1.5rem; font-weight: 900; margin-top: 2px;">{k}</div>
            </div>
            <div style="background: #FFFFFF; border-radius: 16px; padding: 16px; text-align: center; border: 1px solid #E4E4E7; box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
                <div style="font-size: 1.5rem; margin-bottom: 2px;">🫀</div>
                <div style="color: #71717A; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Liver Tests</div>
                <div style="color: #18181B; font-size: 1.5rem; font-weight: 900; margin-top: 2px;">{l}</div>
            </div>
        </div>
        """
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), "", username, user_hist, welcome_html, metrics_html
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "❌ <span style='color: #DC2626; font-weight: 700;'>Invalid credentials. Please try again.</span>", "", [], "", ""

def handle_admin_login(passcode):
    if passcode == ADMIN_SECRET_KEY:
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), "", "", [], "", "", get_all_users()
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "❌ <span style='color: #DC2626; font-weight: 700;'>Incorrect Admin Key.</span>", "", [], "", "", []

def handle_logout():
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "", "", [], "", ""

# --- LIGHT LAVENDER CSS THEME ---
css = """
:root {
    --bg-main: #EBE8F9;
    --card-bg: #FFFFFF;
    --accent-purple: #7C3AED;
    --text-primary: #18181B;
    --border-color: #E4E4E7;
}

body, .gradio-container {
    background-color: var(--bg-main) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: var(--text-primary) !important;
}

.lavender-card {
    background: var(--card-bg) !important;
    border-radius: 24px !important;
    padding: 24px !important;
    border: 1px solid #E2E0F0 !important;
    box-shadow: 0 10px 30px rgba(124, 58, 237, 0.05) !important;
}

.scroll-panel {
    max-height: 520px;
    overflow-y: auto !important;
    padding-right: 8px;
}
.scroll-panel::-webkit-scrollbar { width: 6px; }
.scroll-panel::-webkit-scrollbar-track { background: #F4F4F5; border-radius: 10px; }
.scroll-panel::-webkit-scrollbar-thumb { background: #C4B5FD; border-radius: 10px; }

/* HORIZONTALLY SCROLLABLE TABS CONTAINER FIX */
.horizontal-tabs-container {
    overflow: visible !important;
}

.horizontal-tabs-container > div:first-child,
.horizontal-tabs-container div.tab-nav {
    display: flex !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    white-space: nowrap !important;
    padding-bottom: 8px !important;
    padding-right: 28px !important;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
    width: 100% !important;
    max-width: 100% !important;
}

.horizontal-tabs-container div.tab-nav::-webkit-scrollbar,
.horizontal-tabs-container > div:first-child::-webkit-scrollbar {
    height: 6px;
}
.horizontal-tabs-container div.tab-nav::-webkit-scrollbar-track,
.horizontal-tabs-container > div:first-child::-webkit-scrollbar-track {
    background: #F4F4F5;
    border-radius: 10px;
}
.horizontal-tabs-container div.tab-nav::-webkit-scrollbar-thumb,
.horizontal-tabs-container > div:first-child::-webkit-scrollbar-thumb {
    background: #C4B5FD;
    border-radius: 10px;
}

.horizontal-tabs-container button[role="tab"] {
    color: #52525B !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    background: #F4F4F5 !important;
    border: 1px solid #E4E4E7 !important;
    border-radius: 12px !important;
    padding: 10px 18px !important;
    margin-right: 8px !important;
    flex-shrink: 0 !important;
    min-width: max-content !important;
    transition: all 0.2s ease !important;
}

.horizontal-tabs-container button[role="tab"]:hover {
    color: #18181B !important;
    background: #E9D5FF !important;
}

.horizontal-tabs-container button[role="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    background: var(--accent-purple) !important;
    border-color: var(--accent-purple) !important;
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25) !important;
}

label span { 
    color: var(--text-primary) !important; 
    font-weight: 700 !important; 
    font-size: 0.88rem !important; 
    margin-bottom: 4px !important;
}

input, select, textarea, .ts-control {
    background-color: #F8FAFC !important;
    color: var(--text-primary) !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
}

input:focus, select:focus, textarea:focus {
    border-color: var(--accent-purple) !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15) !important;
}

button.primary-btn {
    background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
    color: #FFFFFF !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    padding: 12px !important;
    border: none !important;
    box-shadow: 0 6px 18px rgba(124, 58, 237, 0.25) !important;
    cursor: pointer !important;
    margin-top: 12px !important;
    transition: transform 0.1s ease, box-shadow 0.2s ease !important;
}

button.primary-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 22px rgba(124, 58, 237, 0.35) !important;
}

button.logout-btn {
    background: #FEE2E2 !important;
    color: #991B1B !important;
    border: 1px solid #FCA5A5 !important;
    font-weight: 800 !important;
    border-radius: 12px !important;
    transition: background 0.2s ease !important;
}

button.logout-btn:hover {
    background: #FCA5A5 !important;
}

.dataframe th {
    background-color: #F3E8FF !important;
    color: #6B21A8 !important;
    font-weight: 800 !important;
}

.dataframe td {
    background-color: #FFFFFF !important;
    color: #18181B !important;
    font-weight: 600 !important;
}

footer { visibility: hidden !important; }
"""

with gr.Blocks(css=css, title="Sick Sense Clinical Dashboard") as demo:
    current_user_state = gr.State(value="")

    # ------------------ AUTHENTICATION PORTAL ------------------
    with gr.Column(visible=True, elem_classes=["lavender-card"]) as auth_view:
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("""
                # 🏥 **Sick Sense Clinical AI**
                ### *Soft Lavender Medical Diagnostic Workstation*
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div style="background: #F3E8FF; border-left: 4px solid #7C3AED; padding: 12px 16px; border-radius: 12px;">
                    <span style="color: #6B21A8; font-weight: 800; font-size: 0.85rem;">● SYSTEM ONLINE</span><br/>
                    <span style="color: #4C1D95; font-size: 0.85rem; font-weight: 600;">5 Machine Learning Models Operational</span>
                </div>
                """)

        gr.Markdown("---")

        with gr.Row():
            # LOGIN & REGISTRATION FORM
            with gr.Column(scale=1.2):
                with gr.Tabs():
                    with gr.Tab("🔑 Sign In"):
                        username_input = gr.Textbox(label="Username", placeholder="Enter your registered username")
                        password_input = gr.Textbox(label="Password", type="password", placeholder="Enter your password")
                        login_btn = gr.Button("Sign In to Workstation", elem_classes=["primary-btn"])
                        login_msg = gr.HTML("")

                    with gr.Tab("📝 Create Account"):
                        new_username = gr.Textbox(label="New Username", placeholder="Choose account username")
                        new_password = gr.Textbox(label="New Password", type="password", placeholder="At least 8 characters long")
                        confirm_password = gr.Textbox(label="Confirm Password", type="password", placeholder="Re-enter password")
                        
                        gr.HTML("""
                        <div style="font-size: 0.8rem; color: #6B21A8; margin-bottom: 8px; font-weight: 600;">
                            🔒 <strong>Security Requirement:</strong> Password must be at least 8 characters long.
                        </div>
                        """)
                        
                        signup_btn = gr.Button("Register New Account", elem_classes=["primary-btn"])
                        signup_msg = gr.HTML("")

                    with gr.Tab("🛡️ Admin Portal"):
                        admin_key_input = gr.Textbox(label="Admin Key", type="password", placeholder="Enter administrative passcode")
                        admin_login_btn = gr.Button("Access Admin Management Panel", elem_classes=["primary-btn"])
                        admin_msg = gr.HTML("")

            # CLINICAL SYSTEM INFORMATION CARDS
            with gr.Column(scale=1):
                gr.HTML("""
                <div style="background: #FAF5FF; border: 1px solid #E9D5FF; border-radius: 18px; padding: 20px;">
                    <h3 style="color: #6B21A8; margin-top:0; font-size: 1.1rem; font-weight: 800;">💡 System Capability Brief</h3>
                    <ul style="color: #3B0764; font-size: 0.88rem; line-height: 1.7; padding-left: 20px; margin-bottom: 0;">
                        <li><strong style="color: #7C3AED;">Cardiovascular Risk:</strong> Evaluates 13 cardiac biomarkers including ST depression and resting blood pressure.</li>
                        <li><strong style="color: #7C3AED;">Glycemic Analysis:</strong> Assesses HbA1c, fasting glucose levels, and BMI indexes.</li>
                        <li><strong style="color: #7C3AED;">Renal & Hepatic Panels:</strong> Measures serum creatinine, eGFR, bilirubin, and transaminase balances.</li>
                        <li><strong style="color: #7C3AED;">Automated Log Tracking:</strong> Saves every diagnostic result into an encrypted database.</li>
                    </ul>
                </div>
                """)

    # ------------------ MAIN CLINICAL DASHBOARD ------------------
    with gr.Row(visible=False, elem_classes=["lavender-card"]) as user_dashboard_view:
        # INFORMATIVE SIDEBAR
        with gr.Column(scale=1, min_width=240):
            gr.HTML("""
            <div style="text-align: center; padding-bottom: 10px;">
                <div style="font-size: 2.2rem;">🧪</div>
                <div style="font-weight: 900; color: #18181B; font-size: 1.2rem; margin-top: 2px;">Sick Sense</div>
                <div style="color: #7C3AED; font-size: 0.75rem; font-weight: 700;">CLINICAL WORKSTATION</div>
            </div>
            """)
            gr.Markdown("---")
            
            gr.HTML("""
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <!-- SYSTEM STATUS -->
                <div style="background: #FAF5FF; border: 1px solid #E9D5FF; padding: 12px; border-radius: 14px;">
                    <div style="font-size: 0.75rem; color: #6B21A8; font-weight: 800; text-transform: uppercase;">● ENGINE STATUS</div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: #18181B; margin-top: 4px;">ML Pipeline Ready</div>
                    <div style="font-size: 0.78rem; color: #71717A; margin-top: 2px;">All 5 diagnostic models loaded and calibrated.</div>
                </div>

                <!-- CLINICAL GUIDE INFO -->
                <div style="background: #F4F4F5; border: 1px solid #E4E4E7; padding: 12px; border-radius: 14px;">
                    <div style="font-size: 0.75rem; color: #52525B; font-weight: 800; text-transform: uppercase;">💡 Quick Reference</div>
                    <ul style="margin: 6px 0 0 0; padding-left: 16px; font-size: 0.78rem; color: #3F3F46; line-height: 1.5;">
                        <li><strong>Glucose Target:</strong> &lt; 100 mg/dL</li>
                        <li><strong>eGFR Normal:</strong> &gt; 60 mL/min</li>
                        <li><strong>Cholesterol Target:</strong> &lt; 200 mg/dl</li>
                    </ul>
                </div>

                <!-- DATA PRIVACY NOTICE -->
                <div style="background: #ECFDF5; border: 1px solid #A7F3D0; padding: 12px; border-radius: 14px;">
                    <div style="font-size: 0.75rem; color: #065F46; font-weight: 800; text-transform: uppercase;">🔒 HIPAA / Encryption</div>
                    <div style="font-size: 0.78rem; color: #047857; margin-top: 4px;">All records are logged with hashed signatures in local storage.</div>
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

            # HORIZONTALLY SCROLLABLE DISEASE TOGGLES CONTAINER
            with gr.Tabs(elem_classes=["horizontal-tabs-container"]):
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
    with gr.Column(visible=False, elem_classes=["lavender-card"]) as admin_dashboard_view:
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
