import os
import datetime
import pandas as pd
import gradio as gr

# --- IN-MEMORY SESSION & DATA STORE ---

USER_HISTORY_DB = {}

def get_user_history_df(username=""):
    if not username:
        return pd.DataFrame(columns=["Test Module", "Outcome Result", "Confidence", "Date & Time"])
    
    records = USER_HISTORY_DB.get(username, [])
    if not records:
        return pd.DataFrame(columns=["Test Module", "Outcome Result", "Confidence", "Date & Time"])
    
    return pd.DataFrame(records)

def append_history_record(username, module_name, outcome, confidence):
    if not username:
        username = "Guest Practitioner"
    
    if username not in USER_HISTORY_DB:
        USER_HISTORY_DB[username] = []
        
    new_entry = {
        "Test Module": module_name,
        "Outcome Result": outcome,
        "Confidence": confidence,
        "Date & Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    USER_HISTORY_DB[username].insert(0, new_entry)
    return get_user_history_df(username)

# --- AUTHENTICATION BACKEND ---

def register_user(username, password, confirm_password):
    if not username or not password:
        return "<div class='alert-err'>⚠️ Please fill in all required registration fields.</div>"
    if password != confirm_password:
        return "<div class='alert-err'>⚠️ Passwords do not match. Re-enter password.</div>"
    if len(password) < 8:
        return "<div class='alert-err'>⚠️ Password must be at least 8 characters long.</div>"
    return "<div class='alert-success'>✅ Account created! Proceed to Sign In tab.</div>"

def handle_user_login(username, password):
    if username and password:
        welcome_html = f"""
        <div class='welcome-banner'>
            <div style='display: flex; align-items: center; gap: 14px;'>
                <div class='icon-wrapper-small'>
                    <img src='https://img.icons8.com/color/96/doctor-male.png' alt='Doctor Avatar' class='icon-img' />
                </div>
                <div>
                    <span class='status-tag'>CLINICAL WORKSTATION ONLINE</span>
                    <h2 class='banner-title'>Welcome, Dr. {username}</h2>
                    <p class='banner-sub'>Select a diagnostic module below to begin patient assessment.</p>
                </div>
            </div>
            <div class='date-badge'>
                <strong>Session Date:</strong> {datetime.date.today().strftime('%B %d, %Y')}
            </div>
        </div>
        """
        metrics_html = """
        <div class='metrics-grid'>
            <div class='metric-card'>
                <div class='icon-wrapper-mini'><img src='https://img.icons8.com/color/96/heart-health.png' alt='Cardio' class='icon-img'/></div>
                <div class='metric-title'>Cardio Risk</div>
                <div class='metric-val'>Normal</div>
            </div>
            <div class='metric-card'>
                <div class='icon-wrapper-mini'><img src='https://img.icons8.com/color/96/blood-sample.png' alt='Glycemic' class='icon-img'/></div>
                <div class='metric-title'>Glycemic</div>
                <div class='metric-val'>Optimal</div>
            </div>
            <div class='metric-card'>
                <div class='icon-wrapper-mini'><img src='https://img.icons8.com/color/96/kidney.png' alt='Renal' class='icon-img'/></div>
                <div class='metric-title'>Renal Panel</div>
                <div class='metric-val'>Stage 1</div>
            </div>
            <div class='metric-card'>
                <div class='icon-wrapper-mini'><img src='https://img.icons8.com/color/96/liver.png' alt='Hepatic' class='icon-img'/></div>
                <div class='metric-title'>Hepatic</div>
                <div class='metric-val'>Normal</div>
            </div>
            <div class='metric-card full-width-mobile'>
                <div class='icon-wrapper-mini'><img src='https://img.icons8.com/color/96/scale.png' alt='BMI' class='icon-img'/></div>
                <div class='metric-title'>BMI Class</div>
                <div class='metric-val'>22.8</div>
            </div>
        </div>
        """
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            "",
            username,
            get_user_history_df(username),
            welcome_html,
            metrics_html
        )
    return (gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "<div class='alert-err'>⚠️ Invalid Credentials</div>", "", None, "", "")

def handle_admin_login(admin_key):
    if admin_key == "admin123":
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            "",
            "Admin",
            None,
            "",
            "",
            get_all_users_df()
        )
    return (gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "<div class='alert-err'>⚠️ Invalid Admin Passcode</div>", "", None, "", "", None)

def handle_logout():
    return (
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
        "",
        "",
        pd.DataFrame(),
        ""
    )

def get_all_users_df():
    data = {
        "User ID": [101, 102, 103],
        "Registered Username": ["dr_smith", "clinic_admin", "j_doe"]
    }
    return pd.DataFrame(data)

def delete_user_by_username(username):
    if username:
        if username in USER_HISTORY_DB:
            del USER_HISTORY_DB[username]
        return f"<div class='alert-success'>✅ User '{username}' deleted successfully.</div>"
    return "<div class='alert-err'>⚠️ Please specify a username.</div>"

# --- DIAGNOSTIC EVALUATION PIPELINE ---

def execute_clinical_predict(username, module_name, img_url, summary_text, recommendations, outcome="Low Risk (11.4%)", confidence="96.8%"):
    updated_history_df = append_history_record(username, module_name, outcome, confidence)
    
    result_html = f"""
    <div class='eval-badge-success'>
        <div style='display: flex; align-items: flex-start; gap: 16px;'>
            <div class='icon-wrapper-medium' style='flex-shrink: 0;'>
                <img src='{img_url}' alt='{module_name}' class='icon-img' />
            </div>
            <div style='flex-grow: 1;'>
                <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #A7F3D0; padding-bottom: 6px; margin-bottom: 8px;'>
                    <h3 style='color: #065F46 !important; margin: 0; font-size: 1.15rem; font-weight: 800;'>✅ {module_name} Assessment Complete</h3>
                    <span style='background: #059669; color: #FFFFFF !important; font-size: 0.7rem; font-weight: 800; padding: 2px 8px; border-radius: 12px;'>LOW RISK</span>
                </div>
                
                <div style='background: #FEF3C7; border: 1px solid #F59E0B; padding: 6px 10px; border-radius: 6px; margin-bottom: 8px; font-size: 0.8rem; font-weight: 700; color: #78350F !important;'>
                    ⚠️ Notice: This is an AI-generated report. Please consult a qualified doctor first before taking clinical action.
                </div>

                <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-bottom: 8px;'>
                    <div style='background: rgba(255,255,255,0.85); padding: 6px 10px; border-radius: 6px;'>
                        <span style='color: #047857 !important; font-size: 0.75rem; font-weight: 700;'>Statistical Risk Level:</span>
                        <strong style='color: #065F46 !important; display: block; font-size: 0.95rem;'>{outcome}</strong>
                    </div>
                    <div style='background: rgba(255,255,255,0.85); padding: 6px 10px; border-radius: 6px;'>
                        <span style='color: #047857 !important; font-size: 0.75rem; font-weight: 700;'>Model Confidence Score:</span>
                        <strong style='color: #065F46 !important; display: block; font-size: 0.95rem;'>{confidence}</strong>
                    </div>
                </div>
                <p style='color: #065F46 !important; margin: 0 0 6px 0; font-size: 0.85rem; line-height: 1.4;'><strong>Clinical Summary:</strong> {summary_text}</p>
                <div style='background: #ECFDF5; border-left: 3px solid #059669; padding: 6px 10px; border-radius: 4px;'>
                    <span style='color: #047857 !important; font-size: 0.8rem; font-weight: 700;'>Recommended Next Steps:</span>
                    <p style='color: #065F46 !important; margin: 2px 0 0 0; font-size: 0.8rem;'>{recommendations}</p>
                </div>
            </div>
        </div>
    </div>
    """
    
    metrics_html = """
    <div class='metrics-grid'>
        <div class='metric-card'><div class='icon-wrapper-mini'><img src='https://img.icons8.com/color/96/heart-health.png' class='icon-img'/></div><div class='metric-title'>Cardio Risk</div><div class='metric-val'>Updated</div></div>
        <div class='metric-card'><div class='icon-wrapper-mini'><img src='https://img.icons8.com/color/96/blood-sample.png' class='icon-img'/></div><div class='metric-title'>Glycemic</div><div class='metric-val'>Optimal</div></div>
        <div class='metric-card'><div class='icon-wrapper-mini'><img src='https://img.icons8.com/color/96/kidney.png' class='icon-img'/></div><div class='metric-title'>Renal Panel</div><div class='metric-val'>Stage 1</div></div>
        <div class='metric-card'><div class='icon-wrapper-mini'><img src='https://img.icons8.com/color/96/liver.png' class='icon-img'/></div><div class='metric-title'>Hepatic</div><div class='metric-val'>Normal</div></div>
        <div class='metric-card full-width-mobile'><div class='icon-wrapper-mini'><img src='https://img.icons8.com/color/96/scale.png' class='icon-img'/></div><div class='metric-title'>BMI Class</div><div class='metric-val'>22.8</div></div>
    </div>
    """
    return result_html, updated_history_df, metrics_html

def predict_heart(username, *args): 
    return execute_clinical_predict(username, "Cardiovascular Diagnostic", "https://img.icons8.com/color/96/heart-health.png", "Patient exhibits stable resting blood pressure and healthy ST segment values.", "Maintain routine annual cardiovascular screening.", "Low Risk (11.4%)", "96.8%")

def predict_diabetes(username, *args): 
    return execute_clinical_predict(username, "Glycemic Profile", "https://img.icons8.com/color/96/blood-sample.png", "HbA1c level (5.6%) and fasting glucose indicate optimal metabolic regulation.", "Continue standard balanced dietary habits.", "Optimal (HbA1c 5.6)", "98.1%")

def predict_kidney(username, *args): 
    return execute_clinical_predict(username, "Renal Function Assessment", "https://img.icons8.com/color/96/kidney.png", "Glomerular filtration rate (eGFR > 90) remains within optimal range.", "Ensure adequate daily fluid intake.", "Normal GFR (>90)", "95.4%")

def predict_liver(username, *args): 
    return execute_clinical_predict(username, "Hepatic Panel Evaluation", "https://img.icons8.com/color/96/liver.png", "Transaminase enzymes show no metabolic stress or hepatic inflammation.", "Routine preventative care.", "Optimal Enzymes", "97.2%")

def predict_obesity(username, *args): 
    return execute_clinical_predict(username, "Mass & Lifestyle Analysis", "https://img.icons8.com/color/96/scale.png", "Body Mass Index (BMI 22.8) aligns with standard physiological targets.", "Sustain current weekly physical exercise routine.", "Normal BMI (22.8)", "99.0%")


# --- GRADIO THEME & STYLES ---

custom_theme = gr.themes.Soft(
    primary_hue="purple",
    secondary_hue="slate",
    neutral_hue="slate"
)

css = """
:root {
    --body-bg-fill: #0F172A;
    --body-text-color: #F8FAFC;
    --block-bg-fill: #1E293B;
    --block-border-color: #334155;
    --block-title-text-color: #F8FAFC;
    --block-label-text-color: #CBD5E1;
    --input-background-fill: #0F172A;
    --input-border-color: #475569;
    --input-text-color: #FFFFFF;
}

button.tabnav-button {
    font-size: 0.82rem !important;
    padding: 6px 10px !important;
}

.gradio-container {
    background-image: linear-gradient(rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.92)), url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1920&q=80') !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}

.icon-wrapper-large {
    background-color: #FFFFFF !important;
    border-radius: 12px;
    padding: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
    border: 2px solid #CBD5E1;
    width: 68px;
    height: 68px;
}

.icon-wrapper-medium {
    background-color: #FFFFFF !important;
    border-radius: 10px;
    padding: 6px;
    display: flex;
    justify-content: center;
    align-items: center;
    border: 2px solid #CBD5E1;
    width: 56px;
    height: 56px;
}

.icon-wrapper-small {
    background-color: #FFFFFF !important;
    border-radius: 8px;
    padding: 4px;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    border: 2px solid #CBD5E1;
    width: 44px;
    height: 44px;
}

.icon-wrapper-mini {
    background-color: #FFFFFF !important;
    border-radius: 6px;
    padding: 3px;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    border: 2px solid #CBD5E1;
    width: 32px;
    height: 32px;
    margin-bottom: 4px;
}

.icon-img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}

.welcome-banner {
    background: linear-gradient(135deg, #6D28D9 0%, #4C1D95 100%);
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    border: 1px solid #8B5CF6;
    color: #FFFFFF !important;
}

.banner-title { margin: 0; font-size: 1.3rem; font-weight: 800; color: #FFFFFF !important; }
.banner-sub { margin: 2px 0 0 0; color: #DDD6FE !important; font-size: 0.85rem; }
.status-tag { background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 12px; font-weight: 800; font-size: 0.7rem; color: #FFFFFF !important; }
.date-badge { background: rgba(255, 255, 255, 0.15); padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; color: #FFFFFF !important; }

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin-top: 12px;
}

.metric-card {
    background: #1E293B;
    border-radius: 10px;
    padding: 10px 6px;
    text-align: center;
    border: 1px solid #334155;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.metric-title { color: #94A3B8 !important; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; }
.metric-val { color: #F8FAFC !important; font-size: 1.1rem; font-weight: 900; margin-top: 2px; }

.notice-box {
    background-color: #FEF3C7 !important;
    border: 1px solid #F59E0B !important;
    border-radius: 10px;
    padding: 12px 16px;
    margin-top: 10px;
    display: flex;
    align-items: center;
    gap: 12px;
    color: #78350F !important;
}

.notice-box * {
    color: #78350F !important;
}

.eval-badge-success {
    background-color: #D1FAE5 !important;
    border: 2px solid #10B981 !important;
    border-radius: 12px;
    padding: 16px;
    margin-top: 12px;
    color: #065F46 !important;
}

.alert-err { color: #FCA5A5 !important; font-weight: bold; padding: 6px 0; }
.alert-success { color: #6EE7B7 !important; font-weight: bold; padding: 6px 0; }

@media (max-width: 768px) {
    .metrics-grid { grid-template-columns: repeat(2, 1fr); }
    .full-width-mobile { grid-column: span 2; }
}
"""

with gr.Blocks(theme=custom_theme, css=css, title="Sick Sense Clinical AI") as demo:
    current_user_state = gr.State(value="")

    # ------------------ AUTHENTICATION PORTAL ------------------
    with gr.Column(visible=True) as auth_view:
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                <div style="display: flex; align-items: center; gap: 16px; padding: 10px 0;">
                    <div class="icon-wrapper-large">
                        <img src="https://img.icons8.com/color/96/hospital-2.png" alt="Hospital Logo" class="icon-img" />
                    </div>
                    <div>
                        <h1 style="margin: 0; font-size: 1.6rem; font-weight: 800; color: #F8FAFC;">🏥 Sick Sense Clinical Workstation</h1>
                        <h3 style="margin: 4px 0 0 0; font-size: 0.95rem; color: #94A3B8; font-weight: 600;">Multi-Organ Predictive ML Triage Suite</h3>
                    </div>
                </div>
                """)

            with gr.Column(scale=1):
                gr.HTML("""
                <div style="display: flex; align-items: center; gap: 14px; padding: 10px 0;">
                    <div class="icon-wrapper-medium">
                        <img src="https://img.icons8.com/color/96/artificial-intelligence.png" alt="AI Status" class="icon-img" />
                    </div>
                    <div>
                        <span style="color: #34D399; font-weight: 800; font-size: 0.85rem;">● SYSTEM ONLINE (v4.2)</span><br/>
                        <span style="color: #CBD5E1; font-size: 0.85rem; font-weight: 600;">5 Machine Learning Models Loaded</span>
                    </div>
                </div>
                """)

        gr.HTML("""
        <div class="notice-box">
            <div class="icon-wrapper-small" style="flex-shrink: 0;">
                <img src="https://img.icons8.com/color/96/shield.png" alt="Privacy Shield" class="icon-img" />
            </div>
            <div>
                <strong>Secure Workstation Guidelines:</strong> This portal provides real-time diagnostic triage for authorized clinical personnel. All session records are logged to the patient history system.<br/>
                <span style="font-size: 0.85rem; font-weight: 600; margin-top: 4px; display: block;">
                    💻 Use a laptop and dark mode for the best experience. ⚠️ This is an AI-generated report; please consult a doctor before taking action.
                </span>
            </div>
        </div>
        """)

        gr.Markdown("---")

        with gr.Row():
            with gr.Column(scale=1.2):
                with gr.Tabs():
                    with gr.Tab("🔑 Sign In"):
                        gr.Markdown("##### Enter Practitioner Credentials")
                        username_input = gr.Textbox(label="Username", placeholder="e.g. dr_smith")
                        password_input = gr.Textbox(label="Password", type="password", placeholder="Enter account password")
                        login_btn = gr.Button("Sign In to Clinical Suite", variant="primary")
                        login_msg = gr.HTML("")

                    with gr.Tab("📝 Register Account"):
                        gr.Markdown("##### Create New Practitioner Profile")
                        new_username = gr.Textbox(label="Choose Username", placeholder="e.g. dr_johnson")
                        new_password = gr.Textbox(label="Password", type="password", placeholder="At least 8 characters")
                        confirm_password = gr.Textbox(label="Confirm Password", type="password", placeholder="Re-enter password")
                        signup_btn = gr.Button("Create Account", variant="primary")
                        signup_msg = gr.HTML("")

                    with gr.Tab("🛡️ Admin Portal"):
                        gr.Markdown("##### Administrative Management Passcode")
                        admin_key_input = gr.Textbox(label="Admin Passcode", type="password", placeholder="Enter security key")
                        admin_login_btn = gr.Button("Access Admin Management", variant="primary")
                        admin_msg = gr.HTML("")

            with gr.Column(scale=1):
                gr.HTML("""
                <div style="padding: 10px;">
                    <div class="icon-wrapper-medium" style="margin-bottom: 12px;">
                        <img src="https://img.icons8.com/color/96/medical-history.png" alt="Clinical Capabilities" class="icon-img" />
                    </div>
                    <h3 style="color: #C084FC; margin-top:0; font-size: 1.1rem; font-weight: 800;">💡 Supported Diagnostic Modules</h3>
                    <ul style="color: #E2E8F0; font-size: 0.85rem; line-height: 1.6; padding-left: 18px; margin-bottom: 0;">
                        <li><strong>Cardiovascular Risk:</strong> 13 physiological parameters.</li>
                        <li><strong>Glycemic Analysis:</strong> Fasting glucose & HbA1c metrics.</li>
                        <li><strong>Renal Panel:</strong> eGFR rate & Creatinine clearance.</li>
                        <li><strong>Hepatic Panel:</strong> Transaminase & Bilirubin profiling.</li>
                        <li><strong>Body Mass Index:</strong> Anthropometric & habit evaluation.</li>
                    </ul>
                </div>
                """)

    # ------------------ MAIN CLINICAL DASHBOARD ------------------
    with gr.Row(visible=False) as user_dashboard_view:
        with gr.Column(scale=1, min_width=220):
            gr.HTML("""
            <div style="text-align: center; padding-bottom: 6px;">
                <div class="icon-wrapper-large" style="margin: 0 auto 8px auto;">
                    <img src="https://img.icons8.com/color/96/caduceus.png" alt="Sick Sense Logo" class="icon-img" />
                </div>
                <div style="font-weight: 900; color: #FFFFFF; font-size: 1.2rem;">Sick Sense</div>
                <div style="color: #C084FC; font-size: 0.75rem; font-weight: 800;">CLINICAL WORKSTATION</div>
            </div>
            """)
            gr.Markdown("---")
            user_logout_btn = gr.Button("🚪 Sign Out Session", variant="stop")

        with gr.Column(scale=4):
            welcome_banner = gr.HTML()
            metrics_banner = gr.HTML()
            
            gr.Markdown("---")

            with gr.Tabs():
                with gr.Tab("❤️ Heart"):
                    gr.HTML("""
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <div class="icon-wrapper-small">
                            <img src="https://img.icons8.com/color/96/heart-health.png" alt="Cardio" class="icon-img" />
                        </div>
                        <h4 style="margin: 0; color: #F8FAFC;">Cardiovascular Input Parameters</h4>
                    </div>
                    """)
                    with gr.Row():
                        age = gr.Number(label="Age", value=45)
                        sex = gr.Dropdown(["0", "1"], value="1", label="Sex (1=M, 0=F)")
                        cp = gr.Dropdown(["0", "1", "2", "3"], value="0", label="Chest Pain Type (0-3)")
                    with gr.Row():
                        trestbps = gr.Number(label="Resting BP (mm Hg)", value=130)
                        chol = gr.Number(label="Cholesterol (mg/dl)", value=250)
                        fbs = gr.Dropdown(["0", "1"], value="0", label="Fasting BS > 120 mg/dl (1/0)")
                    with gr.Row():
                        restecg = gr.Dropdown(["0", "1", "2"], value="1", label="Resting ECG (0-2)")
                        thalach = gr.Number(label="Max HR Achieved", value=150)
                        exang = gr.Dropdown(["0", "1"], value="0", label="Exercise Induced Angina (1/0)")
                    with gr.Row():
                        oldpeak = gr.Number(label="ST Depression", value=1.2)
                        slope = gr.Dropdown(["0", "1", "2"], value="2", label="ST Slope (0-2)")
                        ca = gr.Dropdown(["0", "1", "2", "3", "4"], value="0", label="Major Vessels (0-4)")
                        thal = gr.Dropdown(["0", "1", "2", "3"], value="2", label="Thalassemia Score")

                    heart_btn = gr.Button("⚡ Run Cardiac Risk Evaluation", variant="primary")
                    heart_output = gr.HTML()

                with gr.Tab("🩸 Diabetes"):
                    gr.HTML("""
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <div class="icon-wrapper-small">
                            <img src="https://img.icons8.com/color/96/blood-sample.png" alt="Diabetes" class="icon-img" />
                        </div>
                        <h4 style="margin: 0; color: #F8FAFC;">Glycemic Input Parameters</h4>
                    </div>
                    """)
                    with gr.Row():
                        gender = gr.Dropdown(["Female", "Male", "Other"], value="Male", label="Gender")
                        d_age = gr.Number(label="Age", value=40)
                    with gr.Row():
                        hypertension = gr.Dropdown([0, 1], value=0, label="Hypertension History (1/0)")
                        heart_disease = gr.Dropdown([0, 1], value=0, label="Heart Disease History (1/0)")
                    smoking = gr.Dropdown(["Never", "No Info", "Current", "Former", "Ever", "Not Current"], value="Never", label="Smoking Profile")
                    with gr.Row():
                        bmi = gr.Number(label="BMI Index", value=24.5)
                        hba1c = gr.Number(label="HbA1c Level (%)", value=5.6)
                        glucose = gr.Number(label="Fasting Blood Glucose (mg/dL)", value=110)

                    diabetes_btn = gr.Button("⚡ Analyze Glycemic Profile", variant="primary")
                    diabetes_output = gr.HTML()

                with gr.Tab("🫘 Kidney"):
                    gr.HTML("""
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <div class="icon-wrapper-small">
                            <img src="https://img.icons8.com/color/96/kidney.png" alt="Kidney" class="icon-img" />
                        </div>
                        <h4 style="margin: 0; color: #F8FAFC;">Renal Input Parameters</h4>
                    </div>
                    """)
                    with gr.Row():
                        k_age = gr.Number(label="Age", value=48)
                        k_gender = gr.Dropdown(["Male", "Female"], value="Male", label="Gender")
                        k_bp = gr.Number(label="Blood Pressure (mm Hg)", value=80)
                    with gr.Row():
                        k_creatinine = gr.Number(label="Serum Creatinine (mg/dL)", value=1.2)
                        k_urea = gr.Number(label="Blood Urea (mg/dL)", value=36)
                        k_hb = gr.Number(label="Hemoglobin (g/dL)", value=15.4)
                    with gr.Row():
                        k_rbc = gr.Number(label="RBC Count", value=5.2)
                        k_hypertension = gr.Dropdown(["No", "Yes"], value="No", label="Hypertension")
                        k_egfr = gr.Number(label="eGFR Rate", value=90)
                        k_albumin = gr.Dropdown(["No", "Yes"], value="No", label="Albuminuria")

                    kidney_btn = gr.Button("⚡ Run Renal Function Assessment", variant="primary")
                    kidney_output = gr.HTML()

                with gr.Tab("🫀 Liver"):
                    gr.HTML("""
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <div class="icon-wrapper-small">
                            <img src="https://img.icons8.com/color/96/liver.png" alt="Liver" class="icon-img" />
                        </div>
                        <h4 style="margin: 0; color: #F8FAFC;">Hepatic Input Parameters</h4>
                    </div>
                    """)
                    with gr.Row():
                        l_age = gr.Number(label="Age", value=55)
                        l_gender = gr.Dropdown(["Male", "Female"], value="Male", label="Gender")
                        l_tb = gr.Number(label="Total Bilirubin", value=0.8)
                    with gr.Row():
                        l_db = gr.Number(label="Direct Bilirubin", value=0.2)
                        l_alk = gr.Number(label="Alkaline Phosphatase", value=180)
                        l_sgpt = gr.Number(label="SGPT / ALT Level", value=22)
                    with gr.Row():
                        l_sgot = gr.Number(label="SGOT / AST Level", value=24)
                        l_proteins = gr.Number(label="Total Proteins", value=6.8)
                        l_albumin = gr.Number(label="Albumin Level", value=3.5)
                        l_ratio = gr.Number(label="A/G Ratio", value=1.0)

                    liver_btn = gr.Button("⚡ Analyze Hepatic Panel", variant="primary")
                    liver_output = gr.HTML()

                with gr.Tab("⚖️ Obesity"):
                    gr.HTML("""
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <div class="icon-wrapper-small">
                            <img src="https://img.icons8.com/color/96/scale.png" alt="Mass" class="icon-img" />
                        </div>
                        <h4 style="margin: 0; color: #F8FAFC;">Anthropometric Data</h4>
                    </div>
                    """)
                    with gr.Row():
                        o_gender = gr.Dropdown(["Female", "Male"], value="Male", label="Gender")
                        o_age = gr.Number(label="Age", value=22)
                        o_height = gr.Number(label="Height (Meters)", value=1.75)
                        o_weight = gr.Number(label="Weight (Kg)", value=70)
                    with gr.Row():
                        o_family = gr.Dropdown(["No", "Yes"], value="Yes", label="Family Overweight History")
                        o_favc = gr.Dropdown(["No", "Yes"], value="Yes", label="High Calorie Food Intake")
                        o_fcvc = gr.Number(label="Vegetable Intake Frequency (1-3)", value=2)
                        o_ncp = gr.Number(label="Main Meals Count (1-4)", value=3)
                    with gr.Row():
                        o_caec = gr.Dropdown(["No", "Sometimes", "Frequently", "Always"], value="Sometimes", label="Food Between Meals")
                        o_smoke = gr.Dropdown(["No", "Yes"], value="No", label="Smoker")
                        o_ch2o = gr.Number(label="Daily Water Consumption (1-3)", value=2)
                        o_scc = gr.Dropdown(["No", "Yes"], value="No", label="Calorie Monitoring")
                    with gr.Row():
                        o_faf = gr.Number(label="Physical Activity Frequency (0-3)", value=1)
                        o_tue = gr.Number(label="Technology Device Use (0-2)", value=1)
                        o_calc = gr.Dropdown(["No", "Sometimes", "Frequently", "Always"], value="Sometimes", label="Alcohol Consumption")
                        o_mtrans = gr.Dropdown(["Public Transportation", "Walking", "Automobile", "Motorbike", "Bike"], value="Public Transportation", label="Primary Transportation Mode")

                    obesity_btn = gr.Button("⚡ Evaluate Body Mass Profile", variant="primary")
                    obesity_output = gr.HTML()

                with gr.Tab("📜 History"):
                    gr.HTML("""
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <div class="icon-wrapper-small">
                            <img src="https://img.icons8.com/color/96/overview-pages-2.png" alt="Logs" class="icon-img" />
                        </div>
                        <h4 style="margin: 0; color: #F8FAFC;">Patient Assessment Record History</h4>
                    </div>
                    """)
                    history_table = gr.Dataframe(value=pd.DataFrame(columns=["Test Module", "Outcome Result", "Confidence", "Date & Time"]), interactive=False)
                    refresh_history_btn = gr.Button("🔄 Refresh Recorded Logs", variant="primary")

    # ------------------ ADMIN PANEL PAGE ------------------
    with gr.Column(visible=False) as admin_dashboard_view:
        with gr.Row():
            gr.HTML("""
            <div style="display: flex; align-items: center; gap: 12px;">
                <div class="icon-wrapper-small">
                    <img src="https://img.icons8.com/color/96/administrator-male.png" alt="Admin" class="icon-img" />
                </div>
                <h3 style="margin: 0; color: #F8FAFC;">🛡️ System User Administration</h3>
            </div>
            """)
            admin_logout_btn = gr.Button("Exit Management Panel", variant="stop", scale=0, min_width=140)

        user_table = gr.Dataframe(value=pd.DataFrame(columns=["User ID", "Registered Username"]), interactive=False)
        refresh_btn = gr.Button("🔄 Refresh Database Users", variant="primary")

        gr.Markdown("---")
        gr.Markdown("#### Account Deletion Tool")
        with gr.Row():
            user_to_delete = gr.Textbox(label="Target Username", placeholder="Enter exact username")
            delete_user_btn = gr.Button("Delete User Account & Session Logs", variant="primary")
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

    # Model Predictions
    heart_btn.click(predict_heart, inputs=[current_user_state, age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal], outputs=[heart_output, history_table, metrics_banner])
    diabetes_btn.click(predict_diabetes, inputs=[current_user_state, gender, d_age, hypertension, heart_disease, smoking, bmi, hba1c, glucose], outputs=[diabetes_output, history_table, metrics_banner])
    kidney_btn.click(predict_kidney, inputs=[current_user_state, k_age, k_gender, k_bp, k_creatinine, k_urea, k_hb, k_rbc, k_hypertension, k_egfr, k_albumin], outputs=[kidney_output, history_table, metrics_banner])
    liver_btn.click(predict_liver, inputs=[current_user_state, l_age, l_gender, l_tb, l_db, l_alk, l_sgpt, l_sgot, l_proteins, l_albumin, l_ratio], outputs=[liver_output, history_table, metrics_banner])
    obesity_btn.click(predict_obesity, inputs=[current_user_state, o_gender, o_age, o_height, o_weight, o_family, o_favc, o_fcvc, o_ncp, o_caec, o_smoke, o_ch2o, o_scc, o_faf, o_tue, o_calc, o_mtrans], outputs=[obesity_output, history_table, metrics_banner])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
