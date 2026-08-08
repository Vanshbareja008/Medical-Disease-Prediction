import os
import datetime
import pandas as pd
import gradio as gr

# --- MOCK BACKEND FUNCTIONS FOR DEMO ---

def register_user(username, password, confirm_password):
    if not username or not password:
        return "<p style='color: var(--error-color);'>Please fill in all fields.</p>"
    if password != confirm_password:
        return "<p style='color: var(--error-color);'>Passwords do not match.</p>"
    if len(password) < 8:
        return "<p style='color: var(--error-color);'>Password must be at least 8 characters.</p>"
    return "<p style='color: var(--success-color);'>Account registered successfully! Please sign in.</p>"

def handle_user_login(username, password):
    if username and password:
        welcome_html = f"""
        <div class='welcome-banner'>
            <div>
                <span class='status-tag'>CLINICAL WORKSTATION ONLINE</span>
                <h2 class='welcome-title'>Welcome, {username}</h2>
                <p class='welcome-sub'>Select a diagnostic module below to begin patient assessment.</p>
            </div>
            <div class='date-badge'>
                <strong>Date:</strong> {datetime.date.today().strftime('%B %d, %Y')}
            </div>
        </div>
        """
        metrics_html = """
        <div class='metrics-grid'>
            <div class='metric-card'><div class='metric-icon'>❤️</div><div class='metric-title'>Cardio Risk</div><div class='metric-val'>Normal</div></div>
            <div class='metric-card'><div class='metric-icon'>🩸</div><div class='metric-title'>Glycemic</div><div class='metric-val'>Optimal</div></div>
            <div class='metric-card'><div class='metric-icon'>🫘</div><div class='metric-title'>Renal Panel</div><div class='metric-val'>Stage 1</div></div>
            <div class='metric-card'><div class='metric-icon'>🫀</div><div class='metric-title'>Hepatic</div><div class='metric-val'>Normal</div></div>
            <div class='metric-card full-width-mobile'><div class='metric-icon'>⚖️</div><div class='metric-title'>BMI Class</div><div class='metric-val'>22.8</div></div>
        </div>
        """
        return (
            gr.update(visible=False),  # auth_view
            gr.update(visible=True),   # user_dashboard_view
            gr.update(visible=False),  # admin_dashboard_view
            "",                        # login_msg
            username,                  # current_user_state
            get_user_history_df(username), # history_table
            welcome_html,              # welcome_banner
            metrics_html               # metrics_banner
        )
    return (gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "<p style='color: var(--error-color);'>Invalid credentials</p>", "", None, "", "")

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
    return (gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "<p style='color: var(--error-color);'>Invalid Admin Key</p>", "", None, "", "", None)

def handle_logout():
    return (
        gr.update(visible=True),   # auth_view
        gr.update(visible=False),  # user_dashboard_view
        gr.update(visible=False),  # admin_dashboard_view
        "",                        # clear input 1
        "",                        # clear input 2
        pd.DataFrame(),            # empty history
        ""                         # clear state
    )

def get_user_history_df(username=""):
    data = {
        "Test Module": ["Cardiovascular", "Glycemic Profile"],
        "Outcome Result": ["Low Risk (12%)", "Normal (HbA1c 5.6)"],
        "Confidence": ["94.2%", "98.1%"],
        "Date & Time": ["2026-08-08 10:15", "2026-08-08 10:30"]
    }
    return pd.DataFrame(data)

def get_all_users_df():
    data = {
        "User ID": [101, 102, 103],
        "Registered Username": ["dr_smith", "clinic_admin", "j_doe"]
    }
    return pd.DataFrame(data)

def delete_user_by_username(username):
    if username:
        return f"<p style='color: var(--success-color);'>User '{username}' and associated logs deleted successfully.</p>"
    return "<p style='color: var(--error-color);'>Please specify a username.</p>"

def mock_predict(module_name):
    result_html = f"""
    <div class='eval-badge-success'>
        <h4 style='color: var(--success-header); margin: 0;'>✅ {module_name} Evaluation Complete</h4>
        <p style='color: var(--success-text); margin: 4px 0 0 0; font-size: 0.9rem;'>Risk Level: <strong>Low</strong> | Confidence Score: <strong>96.4%</strong></p>
    </div>
    """
    metrics_html = """
    <div class='metrics-grid'>
        <div class='metric-card'><div class='metric-icon'>❤️</div><div class='metric-title'>Cardio Risk</div><div class='metric-val'>Updated</div></div>
        <div class='metric-card'><div class='metric-icon'>🩸</div><div class='metric-title'>Glycemic</div><div class='metric-val'>Optimal</div></div>
        <div class='metric-card'><div class='metric-icon'>🫘</div><div class='metric-title'>Renal Panel</div><div class='metric-val'>Stage 1</div></div>
        <div class='metric-card'><div class='metric-icon'>🫀</div><div class='metric-title'>Hepatic</div><div class='metric-val'>Normal</div></div>
        <div class='metric-card full-width-mobile'><div class='metric-icon'>⚖️</div><div class='metric-title'>BMI Class</div><div class='metric-val'>22.8</div></div>
    </div>
    """
    return result_html, None, get_user_history_df(), metrics_html

def predict_heart(*args): return mock_predict("Cardiovascular")
def predict_diabetes(*args): return mock_predict("Diabetes")
def predict_kidney(*args): return mock_predict("Kidney Function")
def predict_liver(*args): return mock_predict("Liver Function")
def predict_obesity(*args): return mock_predict("Mass & Lifestyle")


# --- DUAL LIGHT / DARK MODE CSS SYSTEM WITH BACKGROUND IMAGE ---

css = """
/* 1. Global Background Image on Main Wrapper */
.gradio-container {
    background-image: linear-gradient(rgba(15, 23, 42, 0.4), rgba(15, 23, 42, 0.4)), url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1920&q=80') !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
    min-height: 100vh !important;
}

/* 2. Light Mode Glassmorphism Custom Variables */
:root {
    --bg-card: rgba(255, 255, 255, 0.85);
    --bg-card-subtle: rgba(243, 232, 255, 0.75);
    --bg-metric: rgba(255, 255, 255, 0.95);
    --border-color: rgba(226, 224, 240, 0.85);
    --border-subtle: rgba(233, 213, 255, 0.85);
    
    --text-main: #111827;
    --text-muted: #4B5563;
    --text-brand: #6B21A8;
    --text-brand-subtle: #4C1D95;
    
    --input-bg: #FFFFFF;
    --input-text: #111827;
    --input-border: #9CA3AF;
    
    --tab-bg: rgba(244, 244, 245, 0.85);
    --tab-text: #374151;
    --tab-selected-bg: #7C3AED;
    --tab-selected-text: #FFFFFF;
    
    --primary-btn-bg: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
    --primary-btn-text: #FFFFFF;
    
    --logout-bg: rgba(254, 226, 226, 0.9);
    --logout-text: #991B1B;
    --logout-border: #FCA5A5;
    
    --success-bg: rgba(236, 253, 245, 0.95);
    --success-border: #10B981;
    --success-header: #065F46;
    --success-text: #047857;
    --success-color: #10B981;
    --error-color: #EF4444;
    
    --notice-bg: rgba(254, 243, 199, 0.95);
    --notice-border: #FCD34D;
    --notice-text: #92400E;
}

/* 3. Dark Mode Overrides */
.dark, [data-theme="dark"], @media (prefers-color-scheme: dark) {
    :root {
        --bg-card: rgba(24, 24, 27, 0.88);
        --bg-card-subtle: rgba(39, 39, 42, 0.85);
        --bg-metric: rgba(39, 39, 42, 0.9);
        --border-color: rgba(63, 63, 70, 0.85);
        --border-subtle: rgba(82, 82, 91, 0.85);
        
        --text-main: #FAFAFA;
        --text-muted: #D1D5DB;
        --text-brand: #C084FC;
        --text-brand-subtle: #DDD6FE;
        
        --input-bg: #18181B;
        --input-text: #FAFAFA;
        --input-border: #6B7280;
        
        --tab-bg: rgba(39, 39, 42, 0.85);
        --tab-text: #D1D5DB;
        --tab-selected-bg: #8B5CF6;
        --tab-selected-text: #FFFFFF;
        
        --primary-btn-bg: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
        --primary-btn-text: #FFFFFF;
        
        --logout-bg: rgba(69, 10, 10, 0.9);
        --logout-text: #FCA5A5;
        --logout-border: #7F1D1D;
        
        --success-bg: rgba(6, 78, 59, 0.9);
        --success-border: #059669;
        --success-header: #A7F3D0;
        --success-text: #6EE7B7;
        
        --notice-bg: rgba(69, 26, 3, 0.9);
        --notice-border: #78350F;
        --notice-text: #FDE68A;
    }
}

/* 4. Typography & Inputs Adaptations */
.gradio-container p, 
.gradio-container span, 
.gradio-container label, 
.gradio-container .prose,
.gradio-container h1, 
.gradio-container h2, 
.gradio-container h3,
.gradio-container h4 {
    color: var(--text-main) !important;
}

/* Fix input, dropdown, and textarea visibility across themes */
input, textarea, select, .gr-input, .gr-select, 
.gradio-container input, .gradio-container select, .gradio-container textarea {
    color: var(--input-text) !important;
    background-color: var(--input-bg) !important;
    border: 1.5px solid var(--input-border) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* 5. Tab Styling */
button[role="tab"] {
    color: var(--tab-text) !important;
    background: var(--tab-bg) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    padding: 8px 14px !important;
    margin-right: 6px !important;
    font-weight: 700 !important;
    backdrop-filter: blur(6px) !important;
}

button[role="tab"][aria-selected="true"] {
    color: var(--tab-selected-text) !important;
    background-color: var(--tab-selected-bg) !important;
    border-color: var(--tab-selected-bg) !important;
}

/* 6. Custom Glass Card Container */
.lavender-card {
    background: var(--bg-card) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-radius: 20px !important;
    padding: 20px !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15) !important;
}

.scroll-panel {
    max-height: 520px;
    overflow-y: auto !important;
    padding-right: 4px;
}

/* 7. Banner & Metrics */
.welcome-banner {
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.95) 0%, rgba(109, 40, 217, 0.95) 100%);
    backdrop-filter: blur(8px);
    border-radius: 18px;
    padding: 18px 22px;
    color: #FFFFFF !important;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    box-shadow: 0 8px 20px rgba(124, 58, 237, 0.25);
}

.status-tag {
    background: rgba(255,255,255,0.25);
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.75rem;
    margin-bottom: 6px;
    color: #FFFFFF !important;
}

.welcome-title {
    margin: 0;
    font-size: 1.4rem;
    font-weight: 800;
    color: #FFFFFF !important;
}

.welcome-sub {
    margin: 2px 0 0 0;
    color: #F3E8FF !important;
    font-size: 0.85rem;
    font-weight: 500;
}

.date-badge {
    background: rgba(255, 255, 255, 0.2);
    padding: 8px 16px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.3);
    text-align: right;
    color: #FFFFFF !important;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin-top: 14px;
}

.metric-card {
    background: var(--bg-metric);
    backdrop-filter: blur(8px);
    border-radius: 14px;
    padding: 12px 8px;
    text-align: center;
    border: 1px solid var(--border-color);
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.metric-icon {
    font-size: 1.2rem;
}

.metric-title {
    color: var(--text-muted) !important;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
}

.metric-val {
    color: var(--text-main) !important;
    font-size: 1.3rem;
    font-weight: 900;
    margin-top: 2px;
}

.eval-badge-success {
    background: var(--success-bg);
    backdrop-filter: blur(6px);
    border: 1px solid var(--success-border);
    border-radius: 10px;
    padding: 12px;
    margin-top: 10px;
}

.info-banner {
    background: var(--bg-card-subtle);
    backdrop-filter: blur(6px);
    border-left: 4px solid var(--tab-selected-bg);
    padding: 10px 14px;
    border-radius: 10px;
}

.notice-box {
    background: var(--notice-bg);
    backdrop-filter: blur(6px);
    border: 1px solid var(--notice-border);
    border-radius: 12px;
    padding: 10px 14px;
    margin-top: 10px;
    color: var(--notice-text) !important;
    font-size: 0.83rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
}

.notice-box span {
    color: var(--notice-text) !important;
}

/* 8. Button Styling */
button.primary-btn {
    background: var(--primary-btn-bg) !important;
    color: var(--primary-btn-text) !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    padding: 10px !important;
    border: none !important;
    cursor: pointer !important;
    margin-top: 10px !important;
    width: 100% !important;
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3) !important;
}

button.logout-btn {
    background: var(--logout-bg) !important;
    color: var(--logout-text) !important;
    border: 1px solid var(--logout-border) !important;
    font-weight: 800 !important;
    border-radius: 10px !important;
    width: 100% !important;
    backdrop-filter: blur(6px) !important;
}

/* 9. Mobile Responsive Layout Rules */
@media (max-width: 768px) {
    .responsive-auth-container {
        flex-direction: column !important;
        gap: 12px !important;
    }

    .responsive-auth-container > div {
        width: 100% !important;
        min-width: 100% !important;
    }

    .lavender-card {
        padding: 14px !important;
        border-radius: 16px !important;
    }

    input, textarea, select {
        font-size: 16px !important;
        padding: 10px !important;
    }

    .welcome-banner {
        flex-direction: column !important;
        align-items: flex-start !important;
        padding: 14px 16px !important;
        border-radius: 14px !important;
    }

    .welcome-title {
        font-size: 1.15rem !important;
    }

    .welcome-sub {
        font-size: 0.78rem !important;
    }

    .date-badge {
        width: 100% !important;
        text-align: left !important;
        padding: 6px 12px !important;
        margin-top: 4px !important;
    }

    .metrics-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 8px !important;
    }

    .metric-card {
        padding: 10px 6px !important;
    }

    .metric-val {
        font-size: 1.1rem !important;
    }

    .full-width-mobile {
        grid-column: span 2 !important;
    }

    .horizontal-tabs-container button[role="tab"] {
        font-size: 0.75rem !important;
        padding: 6px 10px !important;
        margin-bottom: 4px !important;
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
                <div class="info-banner">
                    <span style="color: var(--text-brand); font-weight: 800; font-size: 0.8rem;">● SYSTEM ONLINE</span><br/>
                    <span style="color: var(--text-brand-subtle); font-size: 0.8rem; font-weight: 600;">5 ML Diagnostic Models Active</span>
                </div>
                """)

        gr.HTML("""
        <div class="notice-box">
            <span style="font-size: 1.1rem;">🎨</span>
            <span><strong>Adaptive Visuals Active:</strong> Translucent glass cards automatically maintain contrast in both <strong>Light Mode</strong> and <strong>Dark Mode</strong> while preserving the fixed background wallpaper.</span>
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
                        
                        gr.HTML("<div style='font-size: 0.78rem; color: var(--text-brand); margin-bottom: 8px;'>🔒 <strong>Requirement:</strong> Minimum 8 characters.</div>")
                        signup_btn = gr.Button("Register Account", elem_classes=["primary-btn"])
                        signup_msg = gr.HTML("")

                    with gr.Tab("🛡️ Admin Portal"):
                        admin_key_input = gr.Textbox(label="Admin Key", type="password", placeholder="Enter admin key")
                        admin_login_btn = gr.Button("Access Admin Panel", elem_classes=["primary-btn"])
                        admin_msg = gr.HTML("")

            with gr.Column(scale=1):
                gr.HTML("""
                <div style="background: var(--bg-card-subtle); border: 1px solid var(--border-subtle); border-radius: 14px; padding: 16px; backdrop-filter: blur(8px);">
                    <h3 style="color: var(--text-brand); margin-top:0; font-size: 1rem; font-weight: 800;">💡 Clinical Triage Capabilities</h3>
                    <ul style="color: var(--text-main); font-size: 0.82rem; line-height: 1.6; padding-left: 16px; margin-bottom: 0;">
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
                <div style="font-weight: 900; color: var(--text-main); font-size: 1.1rem;">Sick Sense</div>
                <div style="color: var(--text-brand); font-size: 0.7rem; font-weight: 700;">CLINICAL WORKSTATION</div>
            </div>
            """)
            gr.Markdown("---")
            
            gr.HTML("""
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <div style="background: var(--bg-card-subtle); border: 1px solid var(--border-subtle); padding: 10px; border-radius: 10px; backdrop-filter: blur(8px);">
                    <div style="font-size: 0.7rem; color: var(--text-brand); font-weight: 800;">● STATUS</div>
                    <div style="font-size: 0.82rem; font-weight: 700; color: var(--text-main);">ML Pipeline Active</div>
                </div>
                <div style="background: var(--tab-bg); border: 1px solid var(--border-subtle); padding: 10px; border-radius: 10px; backdrop-filter: blur(8px);">
                    <div style="font-size: 0.7rem; color: var(--text-muted); font-weight: 800;">💡 Quick Guide</div>
                    <div style="font-size: 0.75rem; color: var(--text-main); margin-top: 4px;">Run predictions under tabs to store patient history dynamically.</div>
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
                        heart_pdf_download = gr.File(label="📄 Download Diagnostic PDF Report", visible=True)

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
                        diabetes_pdf_download = gr.File(label="📄 Download Diagnostic PDF Report", visible=True)

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
                        kidney_pdf_download = gr.File(label="📄 Download Diagnostic PDF Report", visible=True)

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
                        liver_pdf_download = gr.File(label="📄 Download Diagnostic PDF Report", visible=True)

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
                        obesity_pdf_download = gr.File(label="📄 Download Diagnostic PDF Report", visible=True)

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
