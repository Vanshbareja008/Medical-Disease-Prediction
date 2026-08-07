import os
import io
import sqlite3
import hashlib
from datetime import datetime
import gradio as gr
import joblib
import numpy as np
import pandas as pd

# PDF Generation Imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- CONFIGURATION ---
DB_FILE = "users.db"
ADMIN_SECRET_KEY = "admin@123"

# --- DATABASE SETUP ---
def get_db_connection():
    return sqlite3.connect(DB_FILE, timeout=15)

def init_db():
    conn = get_db_connection()
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
            confidence REAL DEFAULT 0.0,
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                       (username, hash_password(password)))
        conn.commit()
        conn.close()
        return "✅ <span style='color: #059669; font-weight: 700;'>Account created successfully! Please Sign In.</span>"
    except sqlite3.IntegrityError:
        return "❌ <span style='color: #DC2626; font-weight: 700;'>Username already exists.</span>"

def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username.strip(),))
    row = cursor.fetchone()
    conn.close()
    return True if row and row[0] == hash_password(password) else False

# --- SAVE & RETRIEVE USER DIAGNOSTIC RECORDS ---
def save_user_record(username, test_type, result_summary, confidence_score):
    if not username:
        return
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO lab_history (username, test_type, result_summary, confidence, timestamp) VALUES (?, ?, ?, ?, ?)",
            (username, test_type, result_summary, confidence_score, time_str)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Write Error: {e}")

def get_user_history_df(username):
    if not username:
        return pd.DataFrame(columns=["Test Module", "Outcome Result", "Confidence", "Date & Time"])
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT test_type, result_summary, confidence, timestamp FROM lab_history WHERE username = ? ORDER BY id DESC", 
            (username,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        formatted_rows = []
        for r in rows:
            conf_str = f"{r[2]:.1f}%" if r[2] else "N/A"
            formatted_rows.append([r[0], r[1], conf_str, r[3]])
            
        return pd.DataFrame(formatted_rows, columns=["Test Module", "Outcome Result", "Confidence", "Date & Time"])
    except Exception as e:
        return pd.DataFrame(columns=["Test Module", "Outcome Result", "Confidence", "Date & Time"])

def get_dashboard_counts(username):
    if not username:
        return 0, 0, 0, 0, 0
    try:
        conn = get_db_connection()
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
    except Exception as e:
        return 0, 0, 0, 0, 0

def get_dashboard_html(username):
    t, h, d, k, l = get_dashboard_counts(username)
    return f"""
    <div class="metrics-grid">
        <div class="metric-card">
            <div style="font-size: 1.2rem;">📊</div>
            <div class="metric-title">Total Tests</div>
            <div class="metric-val">{t}</div>
        </div>
        <div class="metric-card">
            <div style="font-size: 1.2rem;">❤️</div>
            <div class="metric-title">Heart</div>
            <div class="metric-val">{h}</div>
        </div>
        <div class="metric-card">
            <div style="font-size: 1.2rem;">🩸</div>
            <div class="metric-title">Diabetes</div>
            <div class="metric-val">{d}</div>
        </div>
        <div class="metric-card">
            <div style="font-size: 1.2rem;">🫘</div>
            <div class="metric-title">Kidney</div>
            <div class="metric-val">{k}</div>
        </div>
        <div class="metric-card">
            <div style="font-size: 1.2rem;">🫀</div>
            <div class="metric-title">Liver</div>
            <div class="metric-val">{l}</div>
        </div>
    </div>
    """

def get_welcome_banner(username):
    return f"""
    <div style="background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%); border-radius: 18px; padding: 18px 22px; color: #FFFFFF; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; box-shadow: 0 8px 20px rgba(124, 58, 237, 0.2);">
        <div>
            <div style="background: rgba(255,255,255,0.2); display: inline-block; padding: 3px 10px; border-radius: 20px; font-weight: 700; font-size: 0.75rem; margin-bottom: 6px; color: #FFFFFF;">CLINICAL PORTAL ACTIVE</div>
            <h2 style="margin: 0; font-size: 1.4rem; font-weight: 800; color: #FFFFFF;">Welcome, {username}</h2>
            <p style="margin: 2px 0 0 0; color: #F3E8FF; font-size: 0.85rem; font-weight: 500;">Automated health diagnostic triage active.</p>
        </div>
        <div style="background: rgba(255, 255, 255, 0.15); padding: 8px 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.3); text-align: right;">
            <div style="font-size: 0.7rem; color: #E9D5FF; font-weight: 700;">SYSTEM DATE</div>
            <div style="font-size: 0.9rem; font-weight: 800; color: #FFFFFF;">📅 {datetime.now().strftime('%b %d, %Y')}</div>
        </div>
    </div>
    """

# --- ADMIN DATABASE FUNCTIONS ---
def get_all_users_df():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users")
        rows = cursor.fetchall()
        conn.close()
        return pd.DataFrame(rows, columns=["User ID", "Registered Username"])
    except Exception as e:
        return pd.DataFrame(columns=["User ID", "Registered Username"])

def delete_user_by_username(username_to_delete):
    username_to_delete = username_to_delete.strip()
    if not username_to_delete:
        return "❌ <span style='color: #DC2626; font-weight: 700;'>Please enter a valid username.</span>"
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username_to_delete,))
        cursor.execute("DELETE FROM lab_history WHERE username = ?", (username_to_delete,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            return f"✅ <span style='color: #059669; font-weight: 700;'>User '{username_to_delete}' deleted successfully.</span>"
        return "❌ <span style='color: #DC2626; font-weight: 700;'>User not found.</span>"
    except Exception as e:
        return f"❌ <span style='color: #DC2626; font-weight: 700;'>Error deleting user: {e}</span>"

# --- LOAD MODELS ---
heart_model = joblib.load("heart diagn.pkl")
diabetes_model = joblib.load("diabetes diagn.pkl")
kidney_model = joblib.load("kidney diagn.pkl")
liver_model = joblib.load("Liver Diagn.pkl")
obesity_model = joblib.load("Obesity Diagn.pkl")

# --- PDF GENERATOR FUNCTION ---
def generate_medical_pdf(patient_name, test_title, outcome_text, probability_score, biomarkers, recommendations):
    file_path = f"/tmp/{patient_name}_{test_title.replace(' ', '_')}_Report.pdf" if os.name != 'nt' else f"{patient_name}_{test_title.replace(' ', '_')}_Report.pdf"
    
    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, textColor=colors.HexColor('#6D28D9'), spaceAfter=10)
    meta_style = ParagraphStyle('MetaText', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#52525B'), spaceAfter=4)
    heading_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#18181B'), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#27272A'), leading=14, spaceAfter=8)
    warning_style = ParagraphStyle('WarningText', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#991B1B'), leading=13)

    elements = []

    # Title & Metadata
    elements.append(Paragraph(f"Sick Sense Clinical AI — {test_title} Report", title_style))
    elements.append(Paragraph(f"<b>Patient Name:</b> {patient_name} | <b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#7C3AED'), spaceAfter=15))

    # Mandatory Medical Warning Box
    warning_content = [
        Paragraph("<b>⚠️ MANDATORY MEDICAL DISCLAIMER:</b>", warning_style),
        Paragraph("This diagnostic report is generated purely by Machine Learning algorithms for risk stratification support. It DOES NOT constitute a formal medical diagnosis or prescription. You MUST consult a certified medical practitioner/doctor before taking any clinical actions, medication, or lifestyle interventions.", warning_style)
    ]
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#FCA5A5'), spaceAfter=6))
    elements.extend(warning_content)
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#FCA5A5'), spaceBefore=6, spaceAfter=15))

    # Test Results & Confidence Metrics
    elements.append(Paragraph("1. Diagnostic Summary & Model Confidence", heading_style))
    elements.append(Paragraph(f"<b>Primary Outcome:</b> {outcome_text}", body_style))
    elements.append(Paragraph(f"<b>Model Probability / Confidence Index:</b> {probability_score:.1f}%", body_style))

    # Biomarkers Evaluation
    elements.append(Paragraph("2. Evaluated Patient Biomarkers", heading_style))
    elements.append(Paragraph(f"{biomarkers}", body_style))

    # Recommendations
    elements.append(Paragraph("3. Clinical Recommendation & Action Plan", heading_style))
    elements.append(Paragraph(f"{recommendations}", body_style))

    doc.build(elements)
    return file_path

# --- RESULT CARD GENERATOR ---
def create_interactive_result_card(title, value_text, status_label, bar_percent, recommendation, key_biomarkers, risk_level_text, is_risk=False):
    badge_bg = "#FEE2E2" if is_risk else "#DCFCE7"
    badge_color = "#991B1B" if is_risk else "#166534"
    bar_color = "#EF4444" if is_risk else "#7C3AED"

    return f"""
    <div style="background: #FFFFFF; border: 1px solid #E4E4E7; border-radius: 18px; padding: 18px; margin-top: 14px; box-shadow: 0 4px 16px rgba(124, 58, 237, 0.06);">
        <!-- Mandatory Warning Banner -->
        <div style="background: #FEF2F2; border: 1px solid #FCA5A5; border-radius: 10px; padding: 10px 12px; margin-bottom: 12px;">
            <div style="color: #991B1B; font-weight: 800; font-size: 0.78rem; display: flex; align-items: center; gap: 4px;">
                ⚠️ IMPORTANT MEDICAL NOTICE
            </div>
            <div style="color: #7F1D1D; font-size: 0.75rem; margin-top: 2px; line-height: 1.3;">
                This assessment is generated by AI models. <strong>You must consult a certified medical professional</strong> before making any health decisions.
            </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.2rem;">🧪</span>
                <span style="font-weight: 800; color: #18181B; font-size: 1.05rem;">{title}</span>
            </div>
            <span style="background: {badge_bg}; color: {badge_color}; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.75rem; text-transform: uppercase;">
                {status_label}
            </span>
        </div>

        <div style="font-size: 1.2rem; font-weight: 900; color: #18181B; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span style="color: #52525B; font-size: 0.88rem; font-weight: 600;">Outcome:</span> {value_text}
        </div>

        <div style="margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #52525B; font-weight: 700; margin-bottom: 6px;">
                <span>AI Confidence / Risk Index</span>
                <span style="color: {bar_color};">{bar_percent:.1f}% Confidence</span>
            </div>
            <div style="width: 100%; background: #F4F4F5; height: 10px; border-radius: 5px; overflow: hidden; border: 1px solid #E4E4E7;">
                <div style="width: {bar_percent}%; background: {bar_color}; height: 100%; border-radius: 5px; transition: width 0.6s ease-in-out;"></div>
            </div>
        </div>
        
        <details open style="margin-top: 12px; background: #FAF5FF; border-radius: 12px; padding: 12px 14px; border: 1px solid #E9D5FF;">
            <summary style="cursor: pointer; font-weight: 800; color: #6B21A8; font-size: 0.88rem; user-select: none;">
                📊 Biomarker Analysis & Recommendations
            </summary>
            <div style="margin-top: 10px; font-size: 0.85rem; color: #27272A; line-height: 1.5;">
                <div style="margin-bottom: 6px; background: #FFFFFF; padding: 8px 10px; border-radius: 6px; border-left: 3px solid #7C3AED;">
                    <strong style="color: #6B21A8;">Key Biomarkers:</strong><br/>
                    <span style="color: #18181B; font-weight: 600;">{key_biomarkers}</span>
                </div>
                <div style="margin-bottom: 6px; background: #FFFFFF; padding: 8px 10px; border-radius: 6px; border-left: 3px solid {bar_color};">
                    <strong style="color: #6B21A8;">Risk Stratification:</strong><br/>
                    <span style="color: #18181B; font-weight: 600;">{risk_level_text}</span>
                </div>
                <div style="background: #FFFFFF; padding: 8px 10px; border-radius: 6px; border-left: 3px solid #10B981;">
                    <strong style="color: #6B21A8;">Actionable Recommendation:</strong><br/>
                    <span style="color: #18181B; font-weight: 600;">{recommendation}</span>
                </div>
            </div>
        </details>
    </div>
    """

# --- PREDICTION HANDLERS ---
def predict_heart(username, age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal):
    data = np.array([[float(age), float(sex), float(cp), float(trestbps), float(chol),
                      float(fbs), float(restecg), float(thalach), float(exang), 
                      float(oldpeak), float(slope), float(ca), float(thal)]])
    
    probs = heart_model.predict_proba(data)[0]
    res = int(np.argmax(probs))
    conf_score = float(probs[res] * 100)
    
    result_text = "Heart Disease Risk Detected" if res == 1 else "Normal Cardiac Profile"
    save_user_record(username, "Heart Disease", result_text, conf_score)
    
    biomarkers = f"Age: {age} | BP: {trestbps} mm Hg | Chol: {chol} mg/dl | Max HR: {thalach} bpm"
    risk_level = f"High Probability of Cardiovascular Anomaly ({conf_score:.1f}% Confidence)" if res == 1 else f"Low Risk / Standard Baseline ({conf_score:.1f}% Confidence)"
    rec = "Cardiologist consultation advised. Schedule ECG and lipid panel." if res == 1 else "Maintain regular aerobic exercises and annual checks."
    
    card = create_interactive_result_card("Heart Assessment", result_text, "High Risk" if res == 1 else "In-Range", conf_score, rec, biomarkers, risk_level, is_risk=(res == 1))
    pdf_path = generate_medical_pdf(username or "Patient", "Heart Assessment", result_text, conf_score, biomarkers, rec)
    
    return card, gr.update(value=pdf_path, visible=True), get_user_history_df(username), get_dashboard_html(username)

def predict_diabetes(username, gender, age, hypertension, heart_disease, smoking, bmi, hba1c, glucose):
    gender_map = {"Female": 0, "Male": 1, "Other": 2}
    smoke_map = {"Never": 0, "No Info": 1, "Current": 2, "Former": 3, "Ever": 4, "Not Current": 5}
    data = np.array([[gender_map[gender], float(age), float(hypertension), float(heart_disease),
                      smoke_map[smoking], float(bmi), float(hba1c), float(glucose)]])
    
    probs = diabetes_model.predict_proba(data)[0]
    res = int(np.argmax(probs))
    conf_score = float(probs[res] * 100)
    
    result_text = "Elevated Diabetes Risk" if res == 1 else "Normal Glycemic Baseline"
    save_user_record(username, "Diabetes Analysis", result_text, conf_score)
    
    biomarkers = f"HbA1c: {hba1c}% | Fasting Glucose: {glucose} mg/dL | BMI: {bmi}"
    risk_level = f"Hyperglycemia Risk ({conf_score:.1f}% Confidence)" if res == 1 else f"Normoglycemic Baseline ({conf_score:.1f}% Confidence)"
    rec = "Consult an endocrinologist for OGTT and dietary planning." if res == 1 else "Maintain low-glycemic diet and active routine."
    
    card = create_interactive_result_card("Diabetes Assessment", result_text, "Action Required" if res == 1 else "In-Range", conf_score, rec, biomarkers, risk_level, is_risk=(res == 1))
    pdf_path = generate_medical_pdf(username or "Patient", "Diabetes Assessment", result_text, conf_score, biomarkers, rec)
    
    return card, gr.update(value=pdf_path, visible=True), get_user_history_df(username), get_dashboard_html(username)

def predict_kidney(username, age, gender, bp, creatinine, urea, hb, rbc, hypertension, egfr, albumin):
    data = np.array([[float(age), 1 if gender == "Male" else 0, float(bp), float(creatinine),
                      float(urea), float(hb), float(rbc), 1 if hypertension == "Yes" else 0,
                      float(egfr), 1 if albumin == "Yes" else 0]])
    
    probs = kidney_model.predict_proba(data)[0]
    res = int(np.argmax(probs))
    conf_score = float(probs[res] * 100)
    
    result_text = "Renal Dysfunction Indicator" if res == 1 else "Healthy Kidney Parameters"
    save_user_record(username, "Kidney Function", result_text, conf_score)
    
    biomarkers = f"eGFR: {egfr} | Creatinine: {creatinine} mg/dL | Urea: {urea} mg/dL"
    risk_level = f"Elevated Risk of Chronic Kidney Impairment ({conf_score:.1f}% Confidence)" if res == 1 else f"Optimal Glomerular Filtration Rate ({conf_score:.1f}% Confidence)"
    rec = "Nephrology evaluation recommended. Schedule urinalysis." if res == 1 else "Ensure adequate daily hydration (2-3L water)."
    
    card = create_interactive_result_card("Kidney Panel", result_text, "High Risk" if res == 1 else "In-Range", conf_score, rec, biomarkers, risk_level, is_risk=(res == 1))
    pdf_path = generate_medical_pdf(username or "Patient", "Kidney Assessment", result_text, conf_score, biomarkers, rec)
    
    return card, gr.update(value=pdf_path, visible=True), get_user_history_df(username), get_dashboard_html(username)

def predict_liver(username, age, gender, tb, db, alk, sgpt, sgot, proteins, albumin, ratio):
    data = np.array([[float(age), 1 if gender == "Male" else 0, float(tb), float(db),
                      float(alk), float(sgpt), float(sgot), float(proteins), float(albumin), float(ratio)]])
    
    probs = liver_model.predict_proba(data)[0]
    res = int(np.argmax(probs))
    conf_score = float(probs[res] * 100)
    
    result_text = "Hepatic Enzyme Anomaly" if res == 1 else "Normal Liver Panel"
    save_user_record(username, "Liver Function", result_text, conf_score)
    
    biomarkers = f"Total Bilirubin: {tb} | ALT/SGPT: {sgpt} U/L | AST/SGOT: {sgot} U/L"
    risk_level = f"Elevated Transaminases / Hepatic Stress ({conf_score:.1f}% Confidence)" if res == 1 else f"Balanced Hepatic Biomarkers ({conf_score:.1f}% Confidence)"
    rec = "Schedule an abdominal ultrasound and review enzymes with a doctor." if res == 1 else "Maintain healthy lifestyle habits."
    
    card = create_interactive_result_card("Liver Function", result_text, "Elevated Risk" if res == 1 else "In-Range", conf_score, rec, biomarkers, risk_level, is_risk=(res == 1))
    pdf_path = generate_medical_pdf(username or "Patient", "Liver Assessment", result_text, conf_score, biomarkers, rec)
    
    return card, gr.update(value=pdf_path, visible=True), get_user_history_df(username), get_dashboard_html(username)

def predict_obesity(username, gender, age, height, weight, family, favc, fcvc, ncp, caec, smoke, ch2o, scc, faf, tue, calc, mtrans):
    gender_map, yesno = {"Female": 0, "Male": 1}, {"No": 0, "Yes": 1}
    caec_map = calc_map = {"No": 0, "Sometimes": 1, "Frequently": 2, "Always": 3}
    mtrans_map = {"Public Transportation": 0, "Walking": 1, "Automobile": 2, "Motorbike": 3, "Bike": 4}
    label_map = {0: "Insufficient Weight", 1: "Normal Weight", 2: "Overweight Level I", 3: "Overweight Level II", 4: "Obesity Type I", 5: "Obesity Type II", 6: "Obesity Type III"}
    
    data = np.array([[gender_map[gender], float(age), float(height), float(weight), yesno[family], yesno[favc],
                      float(fcvc), float(ncp), caec_map[caec], yesno[smoke], float(ch2o), yesno[scc],
                      float(faf), float(tue), calc_map[calc], mtrans_map[mtrans]]])
    
    probs = obesity_model.predict_proba(data)[0]
    val = int(np.argmax(probs))
    conf_score = float(probs[val] * 100)
    lbl = label_map[val]
    
    save_user_record(username, "Body Mass", lbl, conf_score)
    
    is_risk = val > 1
    bmi_calc = round(float(weight) / (float(height) ** 2), 2)
    biomarkers = f"Calculated BMI: {bmi_calc} kg/m² | Height: {height}m | Weight: {weight}kg"
    risk_level = f"Classified Category: {lbl} ({conf_score:.1f}% Confidence)"
    rec = "Consult with a registered dietitian for personalized meal planning." if is_risk else "Maintain active lifestyle and current caloric balance."
    
    card = create_interactive_result_card("Body Mass Index", lbl, "Attention" if is_risk else "In-Range", conf_score, rec, biomarkers, risk_level, is_risk=is_risk)
    pdf_path = generate_medical_pdf(username or "Patient", "Body Mass Assessment", lbl, conf_score, biomarkers, rec)
    
    return card, gr.update(value=pdf_path, visible=True), get_user_history_df(username), get_dashboard_html(username)

# --- NAVIGATION HANDLERS ---
def handle_user_login(username, password):
    username = username.strip()
    if verify_user(username, password):
        user_hist = get_user_history_df(username)
        welcome_html = get_welcome_banner(username)
        metrics_html = get_dashboard_html(username)
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), "", username, user_hist, welcome_html, metrics_html
    empty_df = pd.DataFrame(columns=["Test Module", "Outcome Result", "Confidence", "Date & Time"])
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "❌ <span style='color: #DC2626; font-weight: 700;'>Invalid credentials. Please try again.</span>", "", empty_df, "", ""

def handle_admin_login(passcode):
    empty_df = pd.DataFrame(columns=["Test Module", "Outcome Result", "Confidence", "Date & Time"])
    if passcode == ADMIN_SECRET_KEY:
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), "", "", empty_df, "", "", get_all_users_df()
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "❌ <span style='color: #DC2626; font-weight: 700;'>Incorrect Admin Key.</span>", "", empty_df, "", "", pd.DataFrame()

def handle_logout():
    empty_df = pd.DataFrame(columns=["Test Module", "Outcome Result", "Confidence", "Date & Time"])
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "", "", empty_df, "", ""

# --- COMPREHENSIVE CSS (FIXES TEXT VISIBILITY & MOBILE COLUMNS) ---
css = """
:root {
    --bg-main: #EBE8F9 !important;
    --card-bg: #FFFFFF !important;
    --accent-purple: #7C3AED !important;
    --text-primary: #18181B !important;
    --border-color: #E4E4E7 !important;

    /* Override Gradio Dark Theme Variable Defaults to Force High Contrast */
    --body-text-color: #18181B !important;
    --block-label-text-color: #3F3F46 !important;
    --input-text-color: #18181B !important;
    --table-text-color: #18181B !important;
}

body, .gradio-container {
    background-color: var(--bg-main) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #18181B !important;
    padding: 8px !important;
}

/* Force standard dark text color across all Markdown elements */
.gradio-container p, 
.gradio-container span, 
.gradio-container h1, 
.gradio-container h2, 
.gradio-container h3, 
.gradio-container h4, 
.gradio-container label, 
.gradio-container .prose {
    color: #18181B !important;
}

/* Text Input & Dropdown Styling to guarantee readability */
input, textarea, select, .gr-input, .gr-select {
    color: #18181B !important;
    background-color: #FFFFFF !important;
    border: 1px solid #D4D4D8 !important;
    border-radius: 8px !important;
}

label span {
    color: #3F3F46 !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
}

.lavender-card {
    background: var(--card-bg) !important;
    border-radius: 20px !important;
    padding: 20px !important;
    border: 1px solid #E2E0F0 !important;
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.05) !important;
}

.scroll-panel {
    max-height: 520px;
    overflow-y: auto !important;
    padding-right: 4px;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin-top: 14px;
}

.metric-card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 12px 8px;
    text-align: center;
    border: 1px solid #E4E4E7;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.metric-title {
    color: #71717A !important;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
}

.metric-val {
    color: #18181B !important;
    font-size: 1.3rem;
    font-weight: 900;
    margin-top: 2px;
}

.horizontal-tabs-container button[role="tab"] {
    color: #52525B !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    background: #F4F4F5 !important;
    border: 1px solid #E4E4E7 !important;
    border-radius: 10px !important;
    padding: 8px 14px !important;
    margin-right: 6px !important;
}

.horizontal-tabs-container button[role="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    background: var(--accent-purple) !important;
    border-color: var(--accent-purple) !important;
}

button.primary-btn {
    background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
    color: #FFFFFF !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    padding: 10px !important;
    border: none !important;
    cursor: pointer !important;
    margin-top: 10px !important;
    width: 100% !important;
}

button.logout-btn {
    background: #FEE2E2 !important;
    color: #991B1B !important;
    border: 1px solid #FCA5A5 !important;
    font-weight: 800 !important;
    border-radius: 10px !important;
    width: 100% !important;
}

/* MOBILE RESPONSIVE OVERRIDES */
@media (max-width: 768px) {
    /* Stack horizontal login columns vertically on phones */
    .responsive-auth-container {
        flex-direction: column !important;
        gap: 16px !important;
    }

    .responsive-auth-container > div {
        width: 100% !important;
        min-width: 100% !important;
    }

    .metrics-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 8px !important;
    }
    
    .metric-card:last-child {
        grid-column: span 2;
    }

    .horizontal-tabs-container button[role="tab"] {
        font-size: 0.75rem !important;
        padding: 6px 10px !important;
        margin-bottom: 4px !important;
    }

    .lavender-card {
        padding: 12px !important;
        border-radius: 14px !important;
    }
}
"""

with gr.Blocks(css=css, title="Sick Sense Clinical Dashboard") as demo:
    current_user_state = gr.State(value="")

    # ------------------ AUTHENTICATION PORTAL ------------------
    with gr.Column(visible=True, elem_classes=["lavender-card"]) as auth_view:
        with gr.Row(elem_classes=["responsive-auth-container"]):
            with gr.Column(scale=1):
                gr.Markdown("""
                # 🏥 **Sick Sense Clinical AI**
                ### *Mobile & Desktop Diagnostic Dashboard*
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div style="background: #F3E8FF; border-left: 4px solid #7C3AED; padding: 10px 14px; border-radius: 10px;">
                    <span style="color: #6B21A8; font-weight: 800; font-size: 0.8rem;">● SYSTEM ONLINE</span><br/>
                    <span style="color: #4C1D95; font-size: 0.8rem; font-weight: 600;">5 ML Diagnostic Models Active</span>
                </div>
                """)

        gr.Markdown("---")

        with gr.Row(elem_classes=["responsive-auth-container"]):
            with gr.Column(scale=1.2):
                with gr.Tabs():
                    with gr.Tab("🔑 Sign In"):
                        username_input = gr.Textbox(label="Username", placeholder="Enter username")
                        password_input = gr.Textbox(label="Password", type="password", placeholder="Enter password")
                        login_btn = gr.Button("Sign In to Workstation", elem_classes=["primary-btn"])
                        login_msg = gr.HTML("")

                    with gr.Tab("📝 Create Account"):
                        new_username = gr.Textbox(label="New Username", placeholder="Choose username")
                        new_password = gr.Textbox(label="New Password", type="password", placeholder="At least 8 characters")
                        confirm_password = gr.Textbox(label="Confirm Password", type="password", placeholder="Re-enter password")
                        
                        gr.HTML("<div style='font-size: 0.78rem; color: #6B21A8; margin-bottom: 8px;'>🔒 <strong>Requirement:</strong> Minimum 8 characters.</div>")
                        signup_btn = gr.Button("Register Account", elem_classes=["primary-btn"])
                        signup_msg = gr.HTML("")

                    with gr.Tab("🛡️ Admin Portal"):
                        admin_key_input = gr.Textbox(label="Admin Key", type="password", placeholder="Enter admin key")
                        admin_login_btn = gr.Button("Access Admin Panel", elem_classes=["primary-btn"])
                        admin_msg = gr.HTML("")

            with gr.Column(scale=1):
                gr.HTML("""
                <div style="background: #FAF5FF; border: 1px solid #E9D5FF; border-radius: 14px; padding: 16px;">
                    <h3 style="color: #6B21A8; margin-top:0; font-size: 1rem; font-weight: 800;">💡 Clinical Triage Capabilities</h3>
                    <ul style="color: #3B0764; font-size: 0.82rem; line-height: 1.6; padding-left: 16px; margin-bottom: 0;">
                        <li><strong>Cardiovascular Evaluation:</strong> 13 parameters.</li>
                        <li><strong>Glycemic Analysis:</strong> HbA1c & Fasting Glucose.</li>
                        <li><strong>Renal & Hepatic Panels:</strong> Enzymes & Function.</li>
                        <li><strong>Encrypted History:</strong> Automatic SQLite logging.</li>
                    </ul>
                </div>
                """)

    # ------------------ MAIN CLINICAL DASHBOARD ------------------
    with gr.Row(visible=False, elem_classes=["lavender-card"]) as user_dashboard_view:
        with gr.Column(scale=1, min_width=220):
            gr.HTML("""
            <div style="text-align: center; padding-bottom: 6px;">
                <div style="font-size: 1.8rem;">🧪</div>
                <div style="font-weight: 900; color: #18181B; font-size: 1.1rem;">Sick Sense</div>
                <div style="color: #7C3AED; font-size: 0.7rem; font-weight: 700;">CLINICAL WORKSTATION</div>
            </div>
            """)
            gr.Markdown("---")
            
            gr.HTML("""
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <div style="background: #FAF5FF; border: 1px solid #E9D5FF; padding: 10px; border-radius: 10px;">
                    <div style="font-size: 0.7rem; color: #6B21A8; font-weight: 800;">● STATUS</div>
                    <div style="font-size: 0.82rem; font-weight: 700; color: #18181B;">ML Pipeline Active</div>
                </div>
                <div style="background: #F4F4F5; border: 1px solid #E4E4E7; padding: 10px; border-radius: 10px;">
                    <div style="font-size: 0.7rem; color: #52525B; font-weight: 800;">💡 Quick Guide</div>
                    <div style="font-size: 0.75rem; color: #3F3F46; margin-top: 4px;">Run predictions under tabs to store patient history dynamically.</div>
                </div>
            </div>
            """)
            
            gr.Markdown("---")
            user_logout_btn = gr.Button("🚪 Sign Out", elem_classes=["logout-btn"])

        with gr.Column(scale=4):
            welcome_banner = gr.HTML()
            metrics_banner = gr.HTML()
            
            gr.Markdown("---")

            with gr.Tabs(elem_classes=["horizontal-tabs-container"]):
                with gr.Tab("❤️ Heart Diagnostic"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        gr.Markdown("#### Cardiovascular Input Parameters")
                        with gr.Row():
                            age = gr.Number(label="Age", value=45)
                            sex = gr.Dropdown(["0", "1"], value="1", label="Sex (1=M, 0=F)")
                            cp = gr.Dropdown(["0", "1", "2", "3"], value="0", label="Chest Pain (0-3)")
                        with gr.Row():
                            trestbps = gr.Number(label="Resting BP (mm Hg)", value=130)
                            chol = gr.Number(label="Cholesterol (mg/dl)", value=250)
                            fbs = gr.Dropdown(["0", "1"], value="0", label="Fasting BS > 120 (1/0)")
                        with gr.Row():
                            restecg = gr.Dropdown(["0", "1", "2"], value="1", label="Resting ECG (0-2)")
                            thalach = gr.Number(label="Max HR Achieved", value=150)
                            exang = gr.Dropdown(["0", "1"], value="0", label="Exercise Angina (1/0)")
                        with gr.Row():
                            oldpeak = gr.Number(label="ST Depression", value=1.2)
                            slope = gr.Dropdown(["0", "1", "2"], value="2", label="ST Slope (0-2)")
                            ca = gr.Dropdown(["0", "1", "2", "3", "4"], value="0", label="Vessels Colored (0-4)")
                            thal = gr.Dropdown(["0", "1", "2", "3"], value="2", label="Thalassemia Score")

                        heart_btn = gr.Button("⚡ Run Cardiac Risk Evaluation", elem_classes=["primary-btn"])
                        heart_output = gr.HTML()
                        heart_pdf_download = gr.File(label="📄 Download Diagnostic PDF Report", visible=False)

                with gr.Tab("🩸 Diabetes Diagnostic"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        gr.Markdown("#### Glycemic Input Parameters")
                        with gr.Row():
                            gender = gr.Dropdown(["Female", "Male", "Other"], value="Male", label="Gender")
                            d_age = gr.Number(label="Age", value=40)
                        with gr.Row():
                            hypertension = gr.Dropdown([0, 1], value=0, label="Hypertension (1/0)")
                            heart_disease = gr.Dropdown([0, 1], value=0, label="Heart Disease (1/0)")
                        smoking = gr.Dropdown(["Never", "No Info", "Current", "Former", "Ever", "Not Current"], value="Never", label="Smoking Profile")
                        with gr.Row():
                            bmi = gr.Number(label="BMI Index", value=24.5)
                            hba1c = gr.Number(label="HbA1c (%)", value=5.6)
                            glucose = gr.Number(label="Fasting Glucose (mg/dL)", value=110)

                        diabetes_btn = gr.Button("⚡ Analyze Glycemic Profile", elem_classes=["primary-btn"])
                        diabetes_output = gr.HTML()
                        diabetes_pdf_download = gr.File(label="📄 Download Diagnostic PDF Report", visible=False)

                with gr.Tab("🫘 Kidney Function"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        gr.Markdown("#### Renal Input Parameters")
                        with gr.Row():
                            k_age = gr.Number(label="Age", value=48)
                            k_gender = gr.Dropdown(["Male", "Female"], value="Male", label="Gender")
                            k_bp = gr.Number(label="BP (mm Hg)", value=80)
                        with gr.Row():
                            k_creatinine = gr.Number(label="Creatinine (mg/dL)", value=1.2)
                            k_urea = gr.Number(label="Urea (mg/dL)", value=36)
                            k_hb = gr.Number(label="Hemoglobin (g/dL)", value=15.4)
                        with gr.Row():
                            k_rbc = gr.Number(label="RBC Count", value=5.2)
                            k_hypertension = gr.Dropdown(["No", "Yes"], value="No", label="Hypertension")
                            k_egfr = gr.Number(label="eGFR Rate", value=90)
                            k_albumin = gr.Dropdown(["No", "Yes"], value="No", label="Albumin Urine")

                        kidney_btn = gr.Button("⚡ Run Renal Function Assessment", elem_classes=["primary-btn"])
                        kidney_output = gr.HTML()
                        kidney_pdf_download = gr.File(label="📄 Download Diagnostic PDF Report", visible=False)

                with gr.Tab("🫀 Liver Function"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        gr.Markdown("#### Hepatic Input Parameters")
                        with gr.Row():
                            l_age = gr.Number(label="Age", value=55)
                            l_gender = gr.Dropdown(["Male", "Female"], value="Male", label="Gender")
                            l_tb = gr.Number(label="Total Bilirubin", value=0.8)
                        with gr.Row():
                            l_db = gr.Number(label="Direct Bilirubin", value=0.2)
                            l_alk = gr.Number(label="Alk Phosphatase", value=180)
                            l_sgpt = gr.Number(label="SGPT / ALT Level", value=22)
                        with gr.Row():
                            l_sgot = gr.Number(label="SGOT / AST Level", value=24)
                            l_proteins = gr.Number(label="Total Proteins", value=6.8)
                            l_albumin = gr.Number(label="Albumin Level", value=3.5)
                            l_ratio = gr.Number(label="A/G Ratio", value=1.0)

                        liver_btn = gr.Button("⚡ Analyze Hepatic Panel", elem_classes=["primary-btn"])
                        liver_output = gr.HTML()
                        liver_pdf_download = gr.File(label="📄 Download Diagnostic PDF Report", visible=False)

                with gr.Tab("⚖️ Mass & Lifestyle"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        gr.Markdown("#### Anthropometric Data")
                        with gr.Row():
                            o_gender = gr.Dropdown(["Female", "Male"], value="Male", label="Gender")
                            o_age = gr.Number(label="Age", value=22)
                            o_height = gr.Number(label="Height (Meters)", value=1.75)
                            o_weight = gr.Number(label="Weight (Kg)", value=70)
                        with gr.Row():
                            o_family = gr.Dropdown(["No", "Yes"], value="Yes", label="Family History")
                            o_favc = gr.Dropdown(["No", "Yes"], value="Yes", label="High Caloric Food")
                            o_fcvc = gr.Number(label="Vegetable Intake (1-3)", value=2)
                            o_ncp = gr.Number(label="Main Meals (1-4)", value=3)
                        with gr.Row():
                            o_caec = gr.Dropdown(["No", "Sometimes", "Frequently", "Always"], value="Sometimes", label="Snack Frequency")
                            o_smoke = gr.Dropdown(["No", "Yes"], value="No", label="Smoker")
                            o_ch2o = gr.Number(label="Water Intake (1-3)", value=2)
                            o_scc = gr.Dropdown(["No", "Yes"], value="No", label="Calorie Monitor")
                        with gr.Row():
                            o_faf = gr.Number(label="Activity Frequency (0-3)", value=1)
                            o_tue = gr.Number(label="Screen Time (0-2)", value=1)
                            o_calc = gr.Dropdown(["No", "Sometimes", "Frequently", "Always"], value="Sometimes", label="Alcohol Intake")
                            o_mtrans = gr.Dropdown(["Public Transportation", "Walking", "Automobile", "Motorbike", "Bike"], value="Public Transportation", label="Transportation Mode")

                        obesity_btn = gr.Button("⚡ Analyze Body Mass Profile", elem_classes=["primary-btn"])
                        obesity_output = gr.HTML()
                        obesity_pdf_download = gr.File(label="📄 Download Diagnostic PDF Report", visible=False)

                with gr.Tab("📜 Medical History Log"):
                    with gr.Column(elem_classes=["scroll-panel"]):
                        gr.Markdown("#### Patient Log History")
                        history_table = gr.Dataframe(value=pd.DataFrame(columns=["Test Module", "Outcome Result", "Confidence", "Date & Time"]), interactive=False)
                        refresh_history_btn = gr.Button("🔄 Refresh Saved Records", elem_classes=["primary-btn"])

    # ------------------ ADMIN PANEL PAGE ------------------
    with gr.Column(visible=False, elem_classes=["lavender-card"]) as admin_dashboard_view:
        with gr.Row():
            gr.Markdown("### 🛡️ Administrative Management")
            admin_logout_btn = gr.Button("Exit Panel", elem_classes=["logout-btn"], scale=0, min_width=100)

        with gr.Column(elem_classes=["scroll-panel"]):
            user_table = gr.Dataframe(value=pd.DataFrame(columns=["User ID", "Registered Username"]), interactive=False)
            refresh_btn = gr.Button("🔄 Refresh Database Table", elem_classes=["primary-btn"])

            gr.Markdown("---")
            gr.Markdown("#### Remove User Account")
            with gr.Row():
                user_to_delete = gr.Textbox(label="Target Username", placeholder="Enter exact username")
                delete_user_btn = gr.Button("Delete Account & Logs", elem_classes=["primary-btn"])
            admin_action_msg = gr.HTML("")

    # ------------------ EVENT LISTENERS & BINDINGS ------------------
    signup_btn.click(register_user, inputs=[new_username, new_password, confirm_password], outputs=[signup_msg])
    login_btn.click(handle_user_login, inputs=[username_input, password_input], outputs=[auth_view, user_dashboard_view, admin_dashboard_view, login_msg, current_user_state, history_table, welcome_banner, metrics_banner])
    admin_login_btn.click(handle_admin_login, inputs=[admin_key_input], outputs=[auth_view, user_dashboard_view, admin_dashboard_view, admin_msg, current_user_state, history_table, welcome_banner, metrics_banner, user_table])
    
    user_logout_btn.click(handle_logout, inputs=[], outputs=[auth_view, user_dashboard_view, admin_dashboard_view, username_input, password_input, history_table, current_user_state])
    admin_logout_btn.click(handle_logout, inputs=[], outputs=[auth_view, user_dashboard_view, admin_dashboard_view, admin_key_input, admin_msg, history_table, current_user_state])
    
    refresh_history_btn.click(get_user_history_df, inputs=[current_user_state], outputs=[history_table])
    refresh_btn.click(get_all_users_df, inputs=[], outputs=[user_table])
    delete_user_btn.click(delete_user_by_username, inputs=[user_to_delete], outputs=[admin_action_msg]).then(get_all_users_df, inputs=[], outputs=[user_table])

    # Model Predictions & Dynamic Downloads
    heart_btn.click(predict_heart, inputs=[current_user_state, age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal], outputs=[heart_output, heart_pdf_download, history_table, metrics_banner])
    diabetes_btn.click(predict_diabetes, inputs=[current_user_state, gender, d_age, hypertension, heart_disease, smoking, bmi, hba1c, glucose], outputs=[diabetes_output, diabetes_pdf_download, history_table, metrics_banner])
    kidney_btn.click(predict_kidney, inputs=[current_user_state, k_age, k_gender, k_bp, k_creatinine, k_urea, k_hb, k_rbc, k_hypertension, k_egfr, k_albumin], outputs=[kidney_output, kidney_pdf_download, history_table, metrics_banner])
    liver_btn.click(predict_liver, inputs=[current_user_state, l_age, l_gender, l_tb, l_db, l_alk, l_sgpt, l_sgot, l_proteins, l_albumin, l_ratio], outputs=[liver_output, liver_pdf_download, history_table, metrics_banner])
    obesity_btn.click(predict_obesity, inputs=[current_user_state, o_gender, o_age, o_height, o_weight, o_family, o_favc, o_fcvc, o_ncp, o_caec, o_smoke, o_ch2o, o_scc, o_faf, o_tue, o_calc, o_mtrans], outputs=[obesity_output, obesity_pdf_download, history_table, metrics_banner])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
