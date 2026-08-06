import os
import sqlite3
import hashlib
import gradio as gr
import joblib
import numpy as np

# --- CONFIGURATION ---
DB_FILE = "users.db"
ADMIN_SECRET_KEY = "admin@123"  # Change this to your preferred admin password

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
        return "✅ Account created successfully! Please Sign In."
    except sqlite3.IntegrityError:
        return "❌ Username already exists. Please choose another."

def verify_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username.strip(),))
    row = cursor.fetchone()
    conn.close()
    return True if row and row[0] == hash_password(password) else False

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
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted_count > 0:
        return f"✅ User '{username_to_delete}' deleted successfully."
    return "❌ User not found."

# --- LOAD MODELS ---
heart_model = joblib.load("heart diagn.pkl")
diabetes_model = joblib.load("diabetes diagn.pkl")
kidney_model = joblib.load("kidney diagn.pkl")
liver_model = joblib.load("Liver Diagn.pkl")
obesity_model = joblib.load("Obesity Diagn.pkl")

# --- PREDICTION FUNCTIONS ---
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

# --- NAVIGATION HANDLERS ---
def handle_user_login(username, password):
    if verify_user(username, password):
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), ""
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "❌ Invalid username or password."

def handle_admin_login(passcode):
    if passcode == ADMIN_SECRET_KEY:
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), "", get_all_users()
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "❌ Incorrect Admin Secret Key.", []

def handle_logout():
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "", ""

# --- STYLING ---
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

.main-title { text-align: center; color: #FFFFFF; margin-bottom: 24px; }
.main-title h1 { font-size: 2.5rem; font-weight: 800; margin: 0; line-height: 1.1; }
.main-title p { color: var(--accent-mint); font-size: 1.1rem; font-weight: 500; margin-top: 8px; }

.auth-card { max-width: 460px; margin: 20px auto !important; padding: 24px; }

button[role="tab"] {
    color: #A3E6CD !important; font-weight: 700 !important; font-size: 1.05rem !important;
    background: transparent !important; border: none !important; opacity: 0.85 !important;
}
button[role="tab"]:hover { color: #FFFFFF !important; opacity: 1 !important; }
button[role="tab"][aria-selected="true"] { color: #FFFFFF !important; opacity: 1 !important; border-bottom: 4px solid #A3E6CD !important; }

.block, .form {
    background: var(--card-bg) !important; border-radius: 16px !important;
    border: none !important; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
}

label span, .block label span, span.text-gray-500 { color: var(--text-muted) !important; font-weight: 700 !important; font-size: 0.9rem !important; }
input, select, textarea, .wrapper { background-color: var(--input-bg) !important; color: var(--text-main) !important; font-weight: 600 !important; border: 1px solid #CBD5E1 !important; border-radius: 8px !important; }

button.primary-btn {
    background-color: var(--btn-dark) !important; color: #FFFFFF !important; border-radius: 12px !important;
    font-weight: 800 !important; font-size: 1.1rem !important; padding: 12px !important;
    border: 2px solid var(--accent-mint) !important; cursor: pointer; margin-top: 10px;
}
button.primary-btn:hover { background-color: #0d4a31 !important; color: var(--accent-mint) !important; }

button.logout-btn { background-color: transparent !important; color: #FF8A8A !important; border: 1px solid #FF8A8A !important; font-weight: 700 !important; border-radius: 8px !important; }

.output-box textarea { background-color: #DCFCE7 !important; color: #065F46 !important; font-weight: 800 !important; font-size: 1.2rem !important; text-align: center; }
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

    # ------------------ AUTHENTICATION PORTAL ------------------
    with gr.Column(visible=True, elem_classes=["auth-card"]) as auth_view:
        with gr.Tabs():
            # User Sign In
            with gr.Tab("User Sign In"):
                username_input = gr.Textbox(label="Username", placeholder="Enter username")
                password_input = gr.Textbox(label="Password", type="password", placeholder="Enter password")
                login_btn = gr.Button("Sign In", elem_classes=["primary-btn"])
                login_msg = gr.Markdown("")

            # User Registration
            with gr.Tab("Register Account"):
                new_username = gr.Textbox(label="New Username", placeholder="Choose username")
                new_password = gr.Textbox(label="New Password", type="password", placeholder="Choose password")
                confirm_password = gr.Textbox(label="Confirm Password", type="password", placeholder="Re-enter password")
                signup_btn = gr.Button("Register", elem_classes=["primary-btn"])
                signup_msg = gr.Markdown("")

            # Admin Access Portal
            with gr.Tab("🛡️ Admin Portal"):
                admin_key_input = gr.Textbox(label="Admin Passcode", type="password", placeholder="Enter admin passcode")
                admin_login_btn = gr.Button("Access Database Dashboard", elem_classes=["primary-btn"])
                admin_msg = gr.Markdown("")

    # ------------------ PREDICTION DASHBOARD ------------------
    with gr.Column(visible=False) as user_dashboard_view:
        with gr.Row():
            gr.Markdown("### Welcome! Select a diagnosis category below.")
            user_logout_btn = gr.Button("Log Out", elem_classes=["logout-btn"], scale=0, min_width=100)

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

    # ------------------ ADMIN DASHBOARD PAGE ------------------
    with gr.Column(visible=False) as admin_dashboard_view:
        with gr.Row():
            gr.Markdown("### 🛡️ Secure Admin Database Management")
            admin_logout_btn = gr.Button("Exit Dashboard", elem_classes=["logout-btn"], scale=0, min_width=130)

        with gr.Column():
            gr.Markdown("#### Registered Users in Database")
            user_table = gr.Dataframe(
                headers=["User ID", "Username"],
                value=[],
                interactive=False
            )
            refresh_btn = gr.Button("🔄 Refresh Database View")

            gr.Markdown("---")
            gr.Markdown("#### Delete User Record")
            with gr.Row():
                user_to_delete = gr.Textbox(label="Target Username", placeholder="Enter username to delete")
                delete_user_btn = gr.Button("Remove User", elem_classes=["primary-btn"])
            admin_action_msg = gr.Markdown("")

    # ------------------ EVENT LISTENERS ------------------
    signup_btn.click(
        register_user,
        inputs=[new_username, new_password, confirm_password],
        outputs=[signup_msg]
    )

    login_btn.click(
        handle_user_login,
        inputs=[username_input, password_input],
        outputs=[auth_view, user_dashboard_view, admin_dashboard_view, login_msg]
    )

    admin_login_btn.click(
        handle_admin_login,
        inputs=[admin_key_input],
        outputs=[auth_view, user_dashboard_view, admin_dashboard_view, admin_msg, user_table]
    )

    user_logout_btn.click(
        handle_logout,
        inputs=[],
        outputs=[auth_view, user_dashboard_view, admin_dashboard_view, username_input, password_input]
    )

    admin_logout_btn.click(
        handle_logout,
        inputs=[],
        outputs=[auth_view, user_dashboard_view, admin_dashboard_view, admin_key_input, admin_msg]
    )

    refresh_btn.click(
        get_all_users,
        inputs=[],
        outputs=[user_table]
    )

    delete_user_btn.click(
        delete_user_by_username,
        inputs=[user_to_delete],
        outputs=[admin_action_msg]
    ).then(
        get_all_users,
        inputs=[],
        outputs=[user_table]
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
