import os
import datetime
import pandas as pd
import gradio as gr

# --- MOCK BACKEND FUNCTIONS FOR DEMO ---

def register_user(username, password, confirm_password):
    if not username or not password:
        return "<p style='color: #EF4444; font-weight: bold;'>⚠️ Please fill in all required registration fields.</p>"
    if password != confirm_password:
        return "<p style='color: #EF4444; font-weight: bold;'>⚠️ Passwords do not match. Re-enter password.</p>"
    if len(password) < 8:
        return "<p style='color: #EF4444; font-weight: bold;'>⚠️ Password must be at least 8 characters long.</p>"
    return "<p style='color: #10B981; font-weight: bold;'>✅ Account created! Proceed to Sign In tab.</p>"

def handle_user_login(username, password):
    if username and password:
        welcome_html = f"""
        <div class='welcome-banner'>
            <div style='display: flex; align-items: center; gap: 14px;'>
                <div class='img-block-wrapper-small'>
                    <img src='https://img.icons8.com/color/96/doctor-male.png' alt='Doctor Avatar' class='block-img-contained' />
                </div>
                <div>
                    <span class='status-tag'>CLINICAL WORKSTATION ONLINE</span>
                    <h2 class='welcome-title'>Welcome, Dr. {username}</h2>
                    <p class='welcome-sub'>Select a diagnostic module below to begin patient assessment.</p>
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
                <div class='img-block-wrapper-mini'><img src='https://img.icons8.com/color/96/heart-health.png' alt='Cardio' class='block-img-contained'/></div>
                <div class='metric-title'>Cardio Risk</div>
                <div class='metric-val'>Normal</div>
            </div>
            <div class='metric-card'>
                <div class='img-block-wrapper-mini'><img src='https://img.icons8.com/color/96/blood-sample.png' alt='Glycemic' class='block-img-contained'/></div>
                <div class='metric-title'>Glycemic</div>
                <div class='metric-val'>Optimal</div>
            </div>
            <div class='metric-card'>
                <div class='img-block-wrapper-mini'><img src='https://img.icons8.com/color/96/kidney.png' alt='Renal' class='block-img-contained'/></div>
                <div class='metric-title'>Renal Panel</div>
                <div class='metric-val'>Stage 1</div>
            </div>
            <div class='metric-card'>
                <div class='img-block-wrapper-mini'><img src='https://img.icons8.com/color/96/liver.png' alt='Hepatic' class='block-img-contained'/></div>
                <div class='metric-title'>Hepatic</div>
                <div class='metric-val'>Normal</div>
            </div>
            <div class='metric-card full-width-mobile'>
                <div class='img-block-wrapper-mini'><img src='https://img.icons8.com/color/96/scale.png' alt='BMI' class='block-img-contained'/></div>
                <div class='metric-title'>BMI Class</div>
                <div class='metric-val'>22.8</div>
            </div>
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
    return (gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "<p style='color: #EF4444; font-weight: bold;'>⚠️ Invalid Credentials</p>", "", None, "", "")

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
    return (gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "<p style='color: #EF4444; font-weight: bold;'>⚠️ Invalid Admin Passcode</p>", "", None, "", "", None)

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
        return f"<p style='color: #10B981; font-weight: bold;'>✅ User '{username}' deleted successfully.</p>"
    return "<p style='color: #EF4444; font-weight: bold;'>⚠️ Please specify a username.</p>"

def mock_predict(module_name, img_url, summary_text, recommendations):
    result_html = f"""
    <div class='eval-badge-success'>
        <div style='display: flex; align-items: flex-start; gap: 16px;'>
            <div class='img-block-wrapper-medium' style='flex-shrink: 0;'>
                <img src='{img_url}' alt='{module_name}' class='block-img-contained' />
            </div>
            <div style='flex-grow: 1;'>
                <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #A7F3D0; padding-bottom: 6px; margin-bottom: 8px;'>
                    <h3 style='color: #065F46 !important; margin: 0; font-size: 1.15rem; font-weight: 800;'>✅ {module_name} Assessment Complete</h3>
                    <span style='background: #059669; color: #FFFFFF !important; font-size: 0.7rem; font-weight: 800; padding: 2px 8px; border-radius: 12px;'>LOW RISK</span>
                </div>
                <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-bottom: 8px;'>
                    <div style='background: rgba(255,255,255,0.6); padding: 6px 10px; border-radius: 6px;'>
                        <span style='color: #047857 !important; font-size: 0.75rem; font-weight: 700;'>Statistical Risk Level:</span>
                        <strong style='color: #065F46 !important; display: block; font-size: 0.95rem;'>11.4% (Normal Range)</strong>
                    </div>
                    <div style='background: rgba(255,255,255,0.6); padding: 6px 10px; border-radius: 6px;'>
                        <span style='color: #047857 !important; font-size: 0.75rem; font-weight: 700;'>Model Confidence Score:</span>
                        <strong style='color: #065F46 !important; display: block; font-size: 0.95rem;'>96.8% (XGBoost Pipeline)</strong>
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
        <div class='metric-card'><div class='img-block-wrapper-mini'><img src='https://img.icons8.com/color/96/heart-health.png' class='block-img-contained'/></div><div class='metric-title'>Cardio Risk</div><div class='metric-val'>Updated</div></div>
        <div class='metric-card'><div class='img-block-wrapper-mini'><img src='https://img.icons8.com/color/96/blood-sample.png' class='block-img-contained'/></div><div class='metric-title'>Glycemic</div><div class='metric-val'>Optimal</div></div>
        <div class='metric-card'><div class='img-block-wrapper-mini'><img src='https://img.icons8.com/color/96/kidney.png' class='block-img-contained'/></div><div class='metric-title'>Renal Panel</div><div class='metric-val'>Stage 1</div></div>
        <div class='metric-card'><div class='img-block-wrapper-mini'><img src='https://img.icons8.com/color/96/liver.png' class='block-img-contained'/></div><div class='metric-title'>Hepatic</div><div class='metric-val'>Normal</div></div>
        <div class='metric-card full-width-mobile'><div class='img-block-wrapper-mini'><img src='https://img.icons8.com/color/96/scale.png' class='block-img-contained'/></div><div class='metric-title'>BMI Class</div><div class='metric-val'>22.8</div></div>
    </div>
    """
    return result_html, get_user_history_df(), metrics_html

def predict_heart(*args): 
    return mock_predict(
        "Cardiovascular Diagnostic", 
        "https://img.icons8.com/color/96/heart-health.png",
        "Patient exhibits stable resting blood pressure and healthy ST segment values. No active ischemic markers detected.",
        "Maintain routine annual cardiovascular screening. Re-evaluate if exertional chest pressure occurs."
    )

def predict_diabetes(*args): 
    return mock_predict(
        "Glycemic Profile", 
        "https://img.icons8.com/color/96/blood-sample.png",
        "HbA1c level (5.6%) and fasting glucose indicate optimal metabolic regulation without pre-diabetic elevation.",
        "Continue standard balanced dietary habits and annual glycemic panel checks."
    )

def predict_kidney(*args): 
    return mock_predict(
        "Renal Function Assessment", 
        "https://img.icons8.com/color/96/kidney.png",
        "Glomerular filtration rate (eGFR > 90) and blood urea nitrogen levels remain within optimal physiological parameters.",
        "Ensure adequate daily fluid intake and monitor annual renal panel."
    )

def predict_liver(*args): 
    return mock_predict(
        "Hepatic Panel Evaluation", 
        "https://img.icons8.com/color/96/liver.png",
        "Transaminase enzymes (SGPT/SGOT) and total bilirubin levels show no metabolic stress or hepatic tissue inflammation.",
        "Routine preventative care. No further hepatic diagnostic panel required at this time."
    )

def predict_obesity(*args): 
    return mock_predict(
        "Mass & Lifestyle Analysis", 
        "https://img.icons8.com/color/96/scale.png",
        "Body Mass Index (BMI 22.8) and daily activity levels align with standard healthy physiological targets.",
        "Sustain current weekly physical exercise routine and balanced macronutrient distribution."
    )


# --- ABSOLUTE HIGH-CONTRAST CSS OVERRIDES (THEME IMMUNE) ---

css = """
/* 1. App Level Background Image with Overlay */
.gradio-container {
    background-image: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.75)), url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1920&q=80') !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
    min-height: 100vh !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* 2. Absolute Universal Text Contrast Rules (Overrides system light/dark settings) */
.gradio-container p, 
.gradio-container span, 
.gradio-container label, 
.gradio-container .prose,
.gradio-container h1, 
.gradio-container h2, 
.gradio-container h3,
.gradio-container h4,
.gradio-container h5,
.gradio-container blockquote {
    color: #F8FAFC !important;
}

/* 3. Form Input Controls - Fixed Contrast */
input, textarea, select, .gr-input, .gr-select,
.gradio-container input, .gradio-container select, .gradio-container textarea {
    color: #0F172A !important;
    background-color: #FFFFFF !important;
    border: 2px solid #64748B !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
}

/* 4. Glass Panel Cards */
.lavender-card {
    background: #0F172A !important;
    border-radius: 18px !important;
    padding: 22px !important;
    border: 1px solid #334155 !important;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5) !important;
}

/* 5. Section Block Cards */
.content-block-card {
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    padding: 18px !important;
    margin-bottom: 12px !important;
}

/* 6. Image Containers (Keeps Icons High Contrast) */
.img-block-wrapper-large {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
    padding: 10px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    border: 2px solid #CBD5E1 !important;
}

.img-block-wrapper-medium {
    background-color: #FFFFFF !important;
    border-radius: 10px !important;
    padding: 8px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    border: 2px solid #CBD5E1 !important;
    width: 64px !important;
    height: 64px !important;
}

.img-block-wrapper-small {
    background-color: #FFFFFF !important;
    border-radius: 8px !important;
    padding: 6px !important;
    display: inline-flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 46px !important;
    height: 46px !important;
}

.img-block-wrapper-mini {
    background-color: #FFFFFF !important;
    border-radius: 6px !important;
    padding: 4px !important;
    display: inline-flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 36px !important;
    height: 36px !important;
    margin-bottom: 6px !important;
}

.block-img-contained {
    max-width: 100% !important;
    max-height: 100% !important;
    object-fit: contain !important;
    display: block !important;
}

/* 7. Tabs Styling */
button[role="tab"] {
    color: #CBD5E1 !important;
    background: #1E293B !important;
    border: 1px solid #475569 !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
    margin-right: 6px !important;
    font-weight: 700 !important;
}

button[role="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    background-color: #7C3AED !important;
    border-color: #8B5CF6 !important;
}

/* 8. Dashboard Banners & Metrics */
.welcome-banner {
    background: linear-gradient(135deg, #6D28D9 0%, #4C1D95 100%) !important;
    border-radius: 14px !important;
    padding: 18px 22px !important;
    display: flex !important;
    flex-wrap: wrap !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 12px !important;
    border: 1px solid #8B5CF6 !important;
}

.welcome-title { margin: 0; font-size: 1.35rem; font-weight: 800; color: #FFFFFF !important; }
.welcome-sub { margin: 2px 0 0 0; color: #DDD6FE !important; font-size: 0.85rem; }
.status-tag { background: rgba(255,255,255,0.2); padding: 3px 10px; border-radius: 20px; font-weight: 800; font-size: 0.72rem; color: #FFFFFF !important; }
.date-badge { background: rgba(255, 255, 255, 0.15); padding: 8px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.3); color: #FFFFFF !important; font-size: 0.85rem; }

.metrics-grid {
    display: grid !important;
    grid-template-columns: repeat(5, 1fr) !important;
    gap: 10px !important;
    margin-top: 14px !important;
}

.metric-card {
    background: #1E293B !important;
    border-radius: 12px !important;
    padding: 12px 8px !important;
    text-align: center !important;
    border: 1px solid #334155 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
}

.metric-title { color: #94A3B8 !important; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; }
.metric-val { color: #F8FAFC !important; font-size: 1.15rem; font-weight: 900; margin-top: 2px; }

.eval-badge-success {
    background: #D1FAE5 !important;
    border: 2px solid #10B981 !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin-top: 12px !important;
}

.notice-box {
    background: #FEF3C7 !important;
    border: 1px solid #FCD34D !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    margin-top: 12px !important;
    display: flex !important;
    align-items: center !important;
    gap: 14px !important;
}

.notice-box p, .notice-box span, .notice-box strong, .notice-box div {
    color: #78350F !important;
}

/* 9. Dataframe Fixed Styling */
.gradio-container .dataframe table {
    background-color: #1E293B !important;
    color: #F8FAFC !important;
}

.gradio-container .dataframe th {
    background-color: #0F172A !important;
    color: #A855F7 !important;
    font-weight: 800 !important;
}

.gradio-container .dataframe td {
    color: #F8FAFC !important;
    border-bottom: 1px solid #334155 !important;
}

/* 10. Interactive Buttons */
button.primary-btn {
    background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    padding: 10px !important;
    border: none !important;
    margin-top: 10px !important;
    width: 100% !important;
    cursor: pointer !important;
}

button.logout-btn {
    background: #7F1D1D !important;
    color: #FECACA !important;
    border: 1px solid #991B1B !important;
    font-weight: 800 !important;
    border-radius: 10px !important;
    width: 100% !important;
    cursor: pointer !important;
}

@media (max-width: 768px) {
    .metrics-grid { grid-template-columns: repeat(2, 1fr) !important; }
    .full-width-mobile { grid-column: span 2 !important; }
}
"""

with gr.Blocks(css=css, title="Sick Sense Clinical AI") as demo:
    current_user_state = gr.State(value="")

    # ------------------ AUTHENTICATION PORTAL ------------------
    with gr.Column(visible=True, elem_classes=["lavender-card"]) as auth_view:
        with gr.Row():
            with gr.Column(scale=1, elem_classes=["content-block-card"]):
                gr.HTML("""
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div class="img-block-wrapper-large" style="width: 76px; height: 76px;">
                        <img src="https://img.icons8.com/color/96/hospital-2.png" alt="Hospital Logo" class="block-img-contained" />
                    </div>
                    <div>
                        <h1 style="margin: 0; font-size: 1.6rem; color: #F8FAFC !important; font-weight: 800;">🏥 Sick Sense Clinical Workstation</h1>
                        <h3 style="margin: 4px 0 0 0; font-size: 0.95rem; color: #CBD5E1 !important; font-weight: 600;">Multi-Organ Predictive ML Triage Suite</h3>
                    </div>
                </div>
                """)

            with gr.Column(scale=1, elem_classes=["content-block-card"]):
                gr.HTML("""
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="img-block-wrapper-medium">
                        <img src="https://img.icons8.com/color/96/artificial-intelligence.png" alt="AI Status" class="block-img-contained" />
                    </div>
                    <div>
                        <span style="color: #34D399 !important; font-weight: 800; font-size: 0.85rem;">● SYSTEM ONLINE (v4.2)</span><br/>
                        <span style="color: #E2E8F0 !important; font-size: 0.85rem; font-weight: 600;">5 Machine Learning Models Loaded</span>
                    </div>
                </div>
                """)

        gr.HTML("""
        <div class="notice-box">
            <div class="img-block-wrapper-small" style="flex-shrink: 0;">
                <img src="https://img.icons8.com/color/96/shield.png" alt="Privacy Shield" class="block-img-contained" />
            </div>
            <div>
                <strong>Secure Workstation Guidelines:</strong> This portal provides real-time diagnostic triage for authorized clinical personnel. All session records are logged to the patient history system.
            </div>
        </div>
        """)

        gr.Markdown("---")

        with gr.Row():
            with gr.Column(scale=1.2, elem_classes=["content-block-card"]):
                with gr.Tabs():
                    with gr.Tab("🔑 Sign In"):
                        gr.Markdown("##### Enter Practitioner Credentials")
                        username_input = gr.Textbox(label="Username", placeholder="e.g. dr_smith")
                        password_input = gr.Textbox(label="Password", type="password", placeholder="Enter account password")
                        login_btn = gr.Button("Sign In to Clinical Suite", elem_classes=["primary-btn"])
                        login_msg = gr.HTML("")

                    with gr.Tab("📝 Register Account"):
                        gr.Markdown("##### Create New Practitioner Profile")
                        new_username = gr.Textbox(label="Choose Username", placeholder="e.g. dr_johnson")
                        new_password = gr.Textbox(label="Password", type="password", placeholder="At least 8 characters")
                        confirm_password = gr.Textbox(label="Confirm Password", type="password", placeholder="Re-enter password")
                        
                        gr.HTML("<div style='font-size: 0.8rem; color: #C084FC; margin-bottom: 8px; font-weight: 700;'>🔒 Password Requirements: Minimum 8 characters.</div>")
                        signup_btn = gr.Button("Create Account", elem_classes=["primary-btn"])
                        signup_msg = gr.HTML("")

                    with gr.Tab("🛡️ Admin Portal"):
                        gr.Markdown("##### Administrative Management Passcode")
                        admin_key_input = gr.Textbox(label="Admin Passcode", type="password", placeholder="Enter security key")
                        admin_login_btn = gr.Button("Access Admin Management", elem_classes=["primary-btn"])
                        admin_msg = gr.HTML("")

            with gr.Column(scale=1, elem_classes=["content-block-card"]):
                gr.HTML("""
                <div>
                    <div class="img-block-wrapper-large" style="width: 64px; height: 64px; margin-bottom: 12px;">
                        <img src="https://img.icons8.com/color/96/medical-history.png" alt="Clinical Capabilities" class="block-img-contained" />
                    </div>
                    <h3 style="color: #A855F7 !important; margin-top:0; font-size: 1.1rem; font-weight: 800;">💡 Supported Diagnostic Modules</h3>
                    <ul style="color: #F1F5F9 !important; font-size: 0.85rem; line-height: 1.6; padding-left: 18px; margin-bottom: 0;">
                        <li><strong>Cardiovascular Risk:</strong> 13 physiological parameters.</li>
                        <li><strong>Glycemic Analysis:</strong> Fasting glucose & HbA1c metrics.</li>
                        <li><strong>Renal Panel:</strong> eGFR rate & Creatinine clearance.</li>
                        <li><strong>Hepatic Panel:</strong> Transaminase & Bilirubin profiling.</li>
                        <li><strong>Body Mass Index:</strong> Anthropometric & habit evaluation.</li>
                    </ul>
                </div>
                """)

    # ------------------ MAIN CLINICAL DASHBOARD ------------------
    with gr.Row(visible=False, elem_classes=["lavender-card"]) as user_dashboard_view:
        with gr.Column(scale=1, min_width=220, elem_classes=["content-block-card"]):
            gr.HTML("""
            <div style="text-align: center; padding-bottom: 6px;">
                <div class="img-block-wrapper-large" style="margin: 0 auto 8px auto; width: 68px; height: 68px;">
                    <img src="https://img.icons8.com/color/96/caduceus.png" alt="Sick Sense Logo" class="block-img-contained" />
                </div>
                <div style="font-weight: 900; color: #FFFFFF !important; font-size: 1.2rem;">Sick Sense</div>
                <div style="color: #C084FC !important; font-size: 0.75rem; font-weight: 800;">CLINICAL WORKSTATION</div>
            </div>
            """)
            gr.Markdown("---")
            
            gr.HTML("""
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <div style="background: #0F172A; border: 1px solid #334155; padding: 10px; border-radius: 10px;">
                    <div style="font-size: 0.7rem; color: #34D399; font-weight: 800;">● STATUS</div>
                    <div style="font-size: 0.85rem; font-weight: 700; color: #F8FAFC !important;">ML Models Operational</div>
                </div>
            </div>
            """)
            
            gr.Markdown("---")
            user_logout_btn = gr.Button("🚪 Sign Out Session", elem_classes=["logout-btn"])

        with gr.Column(scale=4):
            welcome_banner = gr.HTML()
            metrics_banner = gr.HTML()
            
            gr.Markdown("---")

            with gr.Tabs():
                with gr.Tab("❤️ Heart Diagnostic"):
                    with gr.Column(elem_classes=["content-block-card"]):
                        gr.HTML("""
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                            <div class="img-block-wrapper-small">
                                <img src="https://img.icons8.com/color/96/heart-health.png" alt="Cardio" class="block-img-contained" />
                            </div>
                            <h4 style="margin: 0;">Cardiovascular Input Parameters</h4>
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

                        heart_btn = gr.Button("⚡ Run Cardiac Risk Evaluation", elem_classes=["primary-btn"])
                        heart_output = gr.HTML()

                with gr.Tab("🩸 Diabetes Diagnostic"):
                    with gr.Column(elem_classes=["content-block-card"]):
                        gr.HTML("""
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                            <div class="img-block-wrapper-small">
                                <img src="https://img.icons8.com/color/96/blood-sample.png" alt="Diabetes" class="block-img-contained" />
                            </div>
                            <h4 style="margin: 0;">Glycemic Input Parameters</h4>
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

                        diabetes_btn = gr.Button("⚡ Analyze Glycemic Profile", elem_classes=["primary-btn"])
                        diabetes_output = gr.HTML()

                with gr.Tab("🫘 Kidney Function"):
                    with gr.Column(elem_classes=["content-block-card"]):
                        gr.HTML("""
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                            <div class="img-block-wrapper-small">
                                <img src="https://img.icons8.com/color/96/kidney.png" alt="Kidney" class="block-img-contained" />
                            </div>
                            <h4 style="margin: 0;">Renal Input Parameters</h4>
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

                        kidney_btn = gr.Button("⚡ Run Renal Function Assessment", elem_classes=["primary-btn"])
                        kidney_output = gr.HTML()

                with gr.Tab("🫀 Liver Function"):
                    with gr.Column(elem_classes=["content-block-card"]):
                        gr.HTML("""
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                            <div class="img-block-wrapper-small">
                                <img src="https://img.icons8.com/color/96/liver.png" alt="Liver" class="block-img-contained" />
                            </div>
                            <h4 style="margin: 0;">Hepatic Input Parameters</h4>
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

                        liver_btn = gr.Button("⚡ Analyze Hepatic Panel", elem_classes=["primary-btn"])
                        liver_output = gr.HTML()

                with gr.Tab("⚖️ Mass & Lifestyle"):
                    with gr.Column(elem_classes=["content-block-card"]):
                        gr.HTML("""
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                            <div class="img-block-wrapper-small">
                                <img src="https://img.icons8.com/color/96/scale.png" alt="Mass" class="block-img-contained" />
                            </div>
                            <h4 style="margin: 0;">Anthropometric Data</h4>
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

                        obesity_btn = gr.Button("⚡ Evaluate Body Mass Profile", elem_classes=["primary-btn"])
                        obesity_output = gr.HTML()

                with gr.Tab("📜 Medical History Log"):
                    with gr.Column(elem_classes=["content-block-card"]):
                        gr.HTML("""
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                            <div class="img-block-wrapper-small">
                                <img src="https://img.icons8.com/color/96/overview-pages-2.png" alt="Logs" class="block-img-contained" />
                            </div>
                            <h4 style="margin: 0;">Patient Assessment Record History</h4>
                        </div>
                        """)
                        history_table = gr.Dataframe(value=pd.DataFrame(columns=["Test Module", "Outcome Result", "Confidence", "Date & Time"]), interactive=False)
                        refresh_history_btn = gr.Button("🔄 Refresh Recorded Logs", elem_classes=["primary-btn"])

    # ------------------ ADMIN PANEL PAGE ------------------
    with gr.Column(visible=False, elem_classes=["lavender-card"]) as admin_dashboard_view:
        with gr.Row():
            gr.HTML("""
            <div style="display: flex; align-items: center; gap: 12px;">
                <div class="img-block-wrapper-small">
                    <img src="https://img.icons8.com/color/96/administrator-male.png" alt="Admin" class="block-img-contained" />
                </div>
                <h3 style="margin: 0;">🛡️ System User Administration</h3>
            </div>
            """)
            admin_logout_btn = gr.Button("Exit Management Panel", elem_classes=["logout-btn"], scale=0, min_width=140)

        with gr.Column(elem_classes=["content-block-card"]):
            user_table = gr.Dataframe(value=pd.DataFrame(columns=["User ID", "Registered Username"]), interactive=False)
            refresh_btn = gr.Button("🔄 Refresh Database Users", elem_classes=["primary-btn"])

            gr.Markdown("---")
            gr.Markdown("#### Account Deletion Tool")
            with gr.Row():
                user_to_delete = gr.Textbox(label="Target Username", placeholder="Enter exact username")
                delete_user_btn = gr.Button("Delete User Account & Session Logs", elem_classes=["primary-btn"])
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
