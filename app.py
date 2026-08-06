import os
import gradio as gr
import joblib
import numpy as np

# Load Models
heart_model = joblib.load("heart diagn.pkl")
diabetes_model = joblib.load("diabetes diagn.pkl")
kidney_model = joblib.load("kidney diagn.pkl")
liver_model = joblib.load("Liver Diagn.pkl")
obesity_model = joblib.load("Obesity Diagn.pkl")

# User Credentials Database (Username: Password)
USERS = {
    "admin": "admin123",
    "doctor": "health2026",
    "user": "password"
}

# Prediction Functions
def predict_heart(age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal):
    data = np.array([[float(age), float(sex), float(cp), float(trestbps), float(chol),
                      float(fbs), float(restecg), float(thalach), float(exang), 
                      float(oldpeak), float(slope), float(ca), float(thal)]])
    return "❤️ Heart Disease Detected" if heart_model.predict(data)[0] == 1 else "✅ No Heart Disease"

def predict_diabetes(gender, age, hypertension, heart_disease, smoking, bmi, hba1c, glucose):
    gender_map = {"Female": 0, "Male": 1, "Other": 2}
    smoke_map = {"Never": 0, "No Info": 1, "Current": 2, "Former": 3, "Ever": 4, "Not Current": 5}
    data = np.array([[gender_map[gender], float(age), float(hypertension), float(heart_disease),
                      smoke_map[smoking], float(bmi), float(hba1c), float(glucose)]])
    return "🩸 Diabetes Detected" if diabetes_model.predict(data)[0] == 1 else "✅ No Diabetes"

def predict_kidney(age, gender, bp, creatinine, urea, hb, rbc, hypertension, egfr, albumin):
    data = np.array([[float(age), 1 if gender == "Male" else 0, float(bp), float(creatinine),
                      float(urea), float(hb), float(rbc), 1 if hypertension == "Yes" else 0,
                      float(egfr), 1 if albumin == "Yes" else 0]])
    return "🫘 Kidney Disease Detected" if kidney_model.predict(data)[0] == 1 else "✅ Healthy Kidney"

def predict_liver(age, gender, tb, db, alk, sgpt, sgot, proteins, albumin, ratio):
    data = np.array([[float(age), 1 if gender == "Male" else 0, float(tb), float(db),
                      float(alk), float(sgpt), float(sgot), float(proteins), float(albumin), float(ratio)]])
    return "🫀 Liver Disease Detected" if liver_model.predict(data)[0] == 1 else "✅ Healthy Liver"

def predict_obesity(gender, age, height, weight, family, favc, fcvc, ncp, caec, smoke, ch2o, scc, faf, tue, calc, mtrans):
    gender_map, yesno = {"Female": 0, "Male": 1}, {"No": 0, "Yes": 1}
    caec_map = calc_map = {"No": 0, "Sometimes": 1, "Frequently": 2, "Always": 3}
    mtrans_map = {"Public Transportation": 0, "Walking": 1, "Automobile": 2, "Motorbike": 3, "Bike": 4}
    label_map = {0: "Insufficient Weight", 1: "Normal Weight", 2: "Overweight Level I", 3: "Overweight Level II", 4: "Obesity Type I", 5: "Obesity Type II", 6: "Obesity Type III"}
    
    data = np.array([[gender_map[gender], float(age), float(height), float(weight), yesno[family], yesno[favc],
                      float(fcvc), float(ncp), caec_map[caec], yesno[smoke], float(ch2o), yesno[scc],
                      float(faf), float(tue), calc_map[calc], mtrans_map[mtrans]]])
    return label_map[int(obesity_model.predict(data)[0])]

# Auth Handlers
def handle_login(username, password):
    if username in USERS and USERS[username] == password:
        return gr.update(visible=False), gr.update(visible=True), ""
    return gr.update(visible=True), gr.update(visible=False), "❌ Invalid username or password."

def handle_logout():
    return gr.update(visible=True), gr.update(visible=False), "", ""

# High-Contrast Custom CSS
css = """
:root {
    --bg-dark: #0A3925;
    --accent-mint: #A3E6CD;
    --card-bg: #FFFFFF;
    --input-bg: #F0FDF4;
    --text-main: #0F172A;
    --text-muted: #334155;
    --btn-dark: #052316;
}

body, .gradio-container {
    background-color: var(--bg-dark) !important;
    font-family: system-ui, -apple-system, sans-serif !important;
}

/* Header */
.main-title {
    text-align: center;
    color: #FFFFFF;
    margin-bottom: 24px;
}
.main-title h1 {
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0;
    line-height: 1.1;
}
.main-title p {
    color: var(--accent-mint);
    font-size: 1.1rem;
    font-weight: 500;
    margin-top: 8px;
}

/* Auth Section */
.login-card {
    max-width: 420px;
    margin: 40px auto !important;
    padding: 24px;
}

/* High-Contrast Tabs Navigation */
button[role="tab"] {
    color: #A3E6CD !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    background: transparent !important;
    border: none !important;
    opacity: 0.85 !important;
}

button[role="tab"]:hover {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

button[role="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    opacity: 1 !important;
    border-bottom: 4px solid #A3E6CD !important;
}

.tabs {
    background: transparent !important;
    border: none !important;
}

.tab-nav {
    border-bottom: 2px solid rgba(163, 230, 205, 0.3) !important;
}

/* Form Container & Input High Contrast */
.block, .form {
    background: var(--card-bg) !important;
    border-radius: 16px !important;
    border: none !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
}

label span, .block label span, span.text-gray-500 {
    color: var(--text-muted) !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
}

input, select, textarea, .wrapper {
    background-color: var(--input-bg) !important;
    color: var(--text-main) !important;
    font-weight: 600 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
}

input:focus, select:focus {
    border-color: #10B981 !important;
    box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
}

/* Primary Action Buttons */
button.primary-btn {
    background-color: var(--btn-dark) !important;
    color: #FFFFFF !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    font-size: 1.1rem !important;
    padding: 14px !important;
    border: 2px solid var(--accent-mint) !important;
    cursor: pointer;
    margin-top: 10px;
}

button.primary-btn:hover {
    background-color: #0d4a31 !important;
    color: var(--accent-mint) !important;
}

/* Logout Button */
button.logout-btn {
    background-color: transparent !important;
    color: #FF8A8A !important;
    border: 1px solid #FF8A8A !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}

/* Result Textbox */
.output-box textarea {
    background-color: #DCFCE7 !important;
    color: #065F46 !important;
    font-weight: 800 !important;
    font-size: 1.2rem !important;
    text-align: center;
}

footer { visibility: hidden !important; }
"""

header = """
<div class="main-title">
    <h1>es<br>so</h1>
    <p><b>Sick Sense</b> — sense your sickness with machine learning</p>
</div>
"""

with gr.Blocks(css=css, title="Sick Sense") as demo:
    gr.HTML(header)

    # ------------------ LOGIN SCREEN (STARTUP) ------------------
    with gr.Column(visible=True, elem_classes=["login-card"]) as login_view:
        gr.Markdown("### 🔒 Sign In to Access Diagnostics")
        username_input = gr.Textbox(label="Username", placeholder="Enter username")
        password_input = gr.Textbox(label="Password", type="password", placeholder="Enter password")
        login_btn = gr.Button("Sign In", elem_classes=["primary-btn"])
        login_msg = gr.Markdown("", elem_id="login-msg")

    # ------------------ PREDICTION DASHBOARD ------------------
    with gr.Column(visible=False) as main_view:
        with gr.Row():
            gr.Markdown("### Welcome back! Select a diagnosis category below.")
            logout_btn = gr.Button("Log Out", elem_classes=["logout-btn"], scale=0, min_width=100)

        with gr.Tabs():
            # Heart Tab
            with gr.Tab("Heart"):
                with gr.Column():
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

                    heart_btn = gr.Button("Analyze Heart Health", elem_classes=["primary-btn"])
                    heart_output = gr.Textbox(label="Result", interactive=False, elem_classes=["output-box"])
                    heart_btn.click(predict_heart, inputs=[age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal], outputs=heart_output)

            # Diabetes Tab
            with gr.Tab("Diabetes"):
                with gr.Column():
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

                    diabetes_btn = gr.Button("Analyze Diabetes Risk", elem_classes=["primary-btn"])
                    diabetes_output = gr.Textbox(label="Result", interactive=False, elem_classes=["output-box"])
                    diabetes_btn.click(predict_diabetes, inputs=[gender, d_age, hypertension, heart_disease, smoking, bmi, hba1c, glucose], outputs=diabetes_output)

            # Kidney Tab
            with gr.Tab("Kidney"):
                with gr.Column():
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

                    kidney_btn = gr.Button("Analyze Kidney Health", elem_classes=["primary-btn"])
                    kidney_output = gr.Textbox(label="Result", interactive=False, elem_classes=["output-box"])
                    kidney_btn.click(predict_kidney, inputs=[k_age, k_gender, k_bp, k_creatinine, k_urea, k_hb, k_rbc, k_hypertension, k_egfr, k_albumin], outputs=kidney_output)

            # Liver Tab
            with gr.Tab("Liver"):
                with gr.Column():
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

                    liver_btn = gr.Button("Analyze Liver Health", elem_classes=["primary-btn"])
                    liver_output = gr.Textbox(label="Result", interactive=False, elem_classes=["output-box"])
                    liver_btn.click(predict_liver, inputs=[l_age, l_gender, l_tb, l_db, l_alk, l_sgpt, l_sgot, l_proteins, l_albumin, l_ratio], outputs=liver_output)

            # Obesity Tab
            with gr.Tab("Obesity"):
                with gr.Column():
                    with gr.Row():
                        o_gender = gr.Dropdown(["Female", "Male"], value="Male", label="Gender")
                        o_age = gr.Number(label="Age", value=21)
                        o_height = gr.Number(label="Height (m)", value=1.70)
                        o_weight = gr.Number(label="Weight (kg)", value=70)
                    with gr.Row():
                        o_family = gr.Dropdown(["No", "Yes"], value="Yes", label="Family Overweight History")
                        o_favc = gr.Dropdown(["No", "Yes"], value="Yes", label="High Caloric Food")
                        o_fcvc = gr.Number(label="Veggie Frequency (1-3)", value=2)
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
                        o_mtrans = gr.Dropdown(["Public Transportation", "Walking", "Automobile", "Motorbike", "Bike"], value="Public Transportation", label="Transport")

                    obesity_btn = gr.Button("Analyze Obesity Category", elem_classes=["primary-btn"])
                    obesity_output = gr.Textbox(label="Result", interactive=False, elem_classes=["output-box"])
                    obesity_btn.click(predict_obesity, inputs=[o_gender, o_age, o_height, o_weight, o_family, o_favc, o_fcvc, o_ncp, o_caec, o_smoke, o_ch2o, o_scc, o_faf, o_tue, o_calc, o_mtrans], outputs=obesity_output)

    # ------------------ EVENT LISTENERS ------------------
    login_btn.click(
        handle_login,
        inputs=[username_input, password_input],
        outputs=[login_view, main_view, login_msg]
    )

    logout_btn.click(
        handle_logout,
        inputs=[],
        outputs=[login_view, main_view, username_input, password_input]
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
