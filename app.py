# =====================================================
# Complete Dashboard Script (Combined & Fixed)
# =====================================================

import gradio as gr
import joblib
import numpy as np

# =====================================================
# Load Models
# =====================================================

heart_model = joblib.load("heart diagn.pkl")
diabetes_model = joblib.load("diabetes diagn.pkl")
kidney_model = joblib.load("kidney diagn.pkl")
liver_model = joblib.load("Liver Diagn.pkl")
obesity_model = joblib.load("Obesity Diagn.pkl")


# =====================================================
# Prediction Functions
# =====================================================

def predict_heart(age, sex, cp, trestbps, chol, fbs,
                  restecg, thalach, exang,
                  oldpeak, slope, ca, thal):

    data = np.array([[float(age), float(sex), float(cp), float(trestbps), float(chol),
                      float(fbs), float(restecg), float(thalach),
                      float(exang), float(oldpeak),
                      float(slope), float(ca), float(thal)]])

    pred = heart_model.predict(data)[0]

    if pred == 1:
        return "❤️ Heart Disease Detected"
    else:
        return "✅ No Heart Disease"


# -----------------------------------------------------

def predict_diabetes(gender, age,
                     hypertension,
                     heart_disease,
                     smoking,
                     bmi,
                     hba1c,
                     glucose):

    gender_map = {
        "Female": 0,
        "Male": 1,
        "Other": 2
    }

    smoke_map = {
        "Never": 0,
        "No Info": 1,
        "Current": 2,
        "Former": 3,
        "Ever": 4,
        "Not Current": 5
    }

    data = np.array([[
        gender_map[gender],
        float(age),
        float(hypertension),
        float(heart_disease),
        smoke_map[smoking],
        float(bmi),
        float(hba1c),
        float(glucose)
    ]])

    pred = diabetes_model.predict(data)[0]

    if pred == 1:
        return "🩸 Diabetes Detected"
    else:
        return "✅ No Diabetes"


# -----------------------------------------------------

def predict_kidney(age,
                   gender,
                   bp,
                   creatinine,
                   urea,
                   hb,
                   rbc,
                   hypertension,
                   egfr,
                   albumin):

    gender = 1 if gender == "Male" else 0
    hypertension = 1 if hypertension == "Yes" else 0
    albumin = 1 if albumin == "Yes" else 0

    data = np.array([[
        float(age),
        gender,
        float(bp),
        float(creatinine),
        float(urea),
        float(hb),
        float(rbc),
        hypertension,
        float(egfr),
        albumin
    ]])

    pred = kidney_model.predict(data)[0]

    if pred == 1:
        return "🫘 Kidney Disease Detected"

    return "✅ Healthy Kidney"


# -----------------------------------------------------

def predict_liver(age,
                  gender,
                  tb,
                  db,
                  alk,
                  sgpt,
                  sgot,
                  proteins,
                  albumin,
                  ratio):

    gender = 1 if gender == "Male" else 0

    data = np.array([[
        float(age),
        gender,
        float(tb),
        float(db),
        float(alk),
        float(sgpt),
        float(sgot),
        float(proteins),
        float(albumin),
        float(ratio)
    ]])

    pred = liver_model.predict(data)[0]

    if pred == 1:
        return "🫀 Liver Disease Detected"

    return "✅ Healthy Liver"


# -----------------------------------------------------

def predict_obesity(gender,
                    age,
                    height,
                    weight,
                    family,
                    favc,
                    fcvc,
                    ncp,
                    caec,
                    smoke,
                    ch2o,
                    scc,
                    faf,
                    tue,
                    calc,
                    mtrans):

    gender_map = {"Female": 0, "Male": 1}

    yesno = {"No": 0, "Yes": 1}

    caec_map = {
        "No": 0,
        "Sometimes": 1,
        "Frequently": 2,
        "Always": 3
    }

    calc_map = {
        "No": 0,
        "Sometimes": 1,
        "Frequently": 2,
        "Always": 3
    }

    mtrans_map = {
        "Public Transportation": 0,
        "Walking": 1,
        "Automobile": 2,
        "Motorbike": 3,
        "Bike": 4
    }

    label_map = {
        0: "Insufficient Weight",
        1: "Normal Weight",
        2: "Overweight Level I",
        3: "Overweight Level II",
        4: "Obesity Type I",
        5: "Obesity Type II",
        6: "Obesity Type III"
    }

    data = np.array([[
        gender_map[gender],
        float(age),
        float(height),
        float(weight),
        yesno[family],
        yesno[favc],
        float(fcvc),
        float(ncp),
        caec_map[caec],
        yesno[smoke],
        float(ch2o),
        yesno[scc],
        float(faf),
        float(tue),
        calc_map[calc],
        mtrans_map[mtrans]
    ]])

    pred = obesity_model.predict(data)[0]

    return label_map[pred]


# =====================================================
# Custom CSS
# =====================================================

css = """
body {
    background: #0f172a;
}
.gradio-container {
    background: #0f172a;
    color: white;
}
.block {
    border-radius: 18px !important;
    border: none !important;
    box-shadow: 0 10px 25px rgba(0,0,0,.30);
}
button {
    background: #16a34a !important;
    color: white !important;
    font-weight: bold;
}
button:hover {
    background: #15803d !important;
}
h1 {
    text-align: center;
    font-size: 40px;
    font-weight: bold;
}
footer {
    visibility: hidden;
}
"""

# =====================================================
# Dashboard Header
# =====================================================

header = """
# 🏥 Medical Disease Prediction Dashboard

### AI Powered Disease Prediction System

**Developed By : Vansh Bareja**
"""

# =====================================================
# Interface
# =====================================================

with gr.Blocks(
    css=css,
    title="Medical Disease Prediction Dashboard"
) as demo:

    gr.Markdown(header)

    with gr.Tabs():

        # =================================================
        # HEART DISEASE
        # =================================================
        with gr.Tab("❤️ Heart Disease"):
            gr.Markdown("## Heart Disease Prediction")
            with gr.Row():
                age = gr.Number(label="Age", value=45)
                sex = gr.Dropdown(["0", "1"], value="1", label="Sex (Male=1 Female=0)")
                cp = gr.Dropdown(["0", "1", "2", "3"], value="0", label="Chest Pain Type")

            with gr.Row():
                trestbps = gr.Number(label="Resting Blood Pressure", value=130)
                chol = gr.Number(label="Cholesterol", value=250)
                fbs = gr.Dropdown(["0", "1"], value="0", label="Fasting Blood Sugar")

            with gr.Row():
                restecg = gr.Dropdown(["0", "1", "2"], value="1", label="Rest ECG")
                thalach = gr.Number(label="Maximum Heart Rate", value=150)
                exang = gr.Dropdown(["0", "1"], value="0", label="Exercise Angina")

            with gr.Row():
                oldpeak = gr.Number(label="Old Peak", value=1.2)
                slope = gr.Dropdown(["0", "1", "2"], value="2", label="Slope")
                ca = gr.Dropdown(["0", "1", "2", "3", "4"], value="0", label="Major Vessels")
                thal = gr.Dropdown(["0", "1", "2", "3"], value="2", label="Thal")

            heart_btn = gr.Button("Predict Heart Disease", variant="primary")
            heart_output = gr.Textbox(label="Prediction")

            heart_btn.click(
                predict_heart,
                inputs=[age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal],
                outputs=heart_output
            )

        # =================================================
        # DIABETES
        # =================================================
        with gr.Tab("🩸 Diabetes"):
            gr.Markdown("## Diabetes Prediction")
            with gr.Row():
                gender = gr.Dropdown(["Female", "Male", "Other"], value="Male", label="Gender")
                d_age = gr.Number(label="Age", value=40)

            with gr.Row():
                hypertension = gr.Dropdown([0, 1], value=0, label="Hypertension")
                heart_disease = gr.Dropdown([0, 1], value=0, label="Heart Disease")

            smoking = gr.Dropdown(
                ["Never", "No Info", "Current", "Former", "Ever", "Not Current"],
                value="Never",
                label="Smoking History"
            )

            with gr.Row():
                bmi = gr.Number(label="BMI", value=24)
                hba1c = gr.Number(label="HbA1c Level", value=5.6)
                glucose = gr.Number(label="Blood Glucose", value=110)

            diabetes_btn = gr.Button("Predict Diabetes", variant="primary")
            diabetes_output = gr.Textbox(label="Prediction")

            diabetes_btn.click(
                predict_diabetes,
                inputs=[gender, d_age, hypertension, heart_disease, smoking, bmi, hba1c, glucose],
                outputs=diabetes_output
            )

        # =================================================
        # KIDNEY DISEASE
        # =================================================
        with gr.Tab("🫘 Kidney Disease"):
            gr.Markdown("## Kidney Disease Prediction")
            with gr.Row():
                k_age = gr.Number(label="Age", value=48)
                k_gender = gr.Dropdown(["Male", "Female"], value="Male", label="Gender")
                k_bp = gr.Number(label="Blood Pressure", value=80)

            with gr.Row():
                k_creatinine = gr.Number(label="Serum Creatinine", value=1.2)
                k_urea = gr.Number(label="Blood Urea", value=36)
                k_hb = gr.Number(label="Hemoglobin", value=15.4)

            with gr.Row():
                k_rbc = gr.Number(label="Red Blood Cells Count", value=5.2)
                k_hypertension = gr.Dropdown(["No", "Yes"], value="No", label="Hypertension")
                k_egfr = gr.Number(label="eGFR", value=90)
                k_albumin = gr.Dropdown(["No", "Yes"], value="No", label="Albumin")

            kidney_btn = gr.Button("Predict Kidney Disease", variant="primary")
            kidney_output = gr.Textbox(label="Prediction")

            kidney_btn.click(
                predict_kidney,
                inputs=[k_age, k_gender, k_bp, k_creatinine, k_urea, k_hb, k_rbc, k_hypertension, k_egfr, k_albumin],
                outputs=kidney_output
            )

        # =================================================
        # LIVER DISEASE
        # =================================================
        with gr.Tab("🫀 Liver Disease"):
            gr.Markdown("## Liver Disease Prediction")
            with gr.Row():
                l_age = gr.Number(label="Age", value=65)
                l_gender = gr.Dropdown(["Male", "Female"], value="Male", label="Gender")
                l_tb = gr.Number(label="Total Bilirubin", value=0.7)

            with gr.Row():
                l_db = gr.Number(label="Direct Bilirubin", value=0.1)
                l_alk = gr.Number(label="Alkaline Phosphatase", value=187)
                l_sgpt = gr.Number(label="Alamine Aminotransferase (SGPT)", value=16)

            with gr.Row():
                l_sgot = gr.Number(label="Aspartate Aminotransferase (SGOT)", value=18)
                l_proteins = gr.Number(label="Total Proteins", value=6.8)
                l_albumin = gr.Number(label="Albumin", value=3.3)
                l_ratio = gr.Number(label="Albumin and Globulin Ratio", value=0.9)

            liver_btn = gr.Button("Predict Liver Disease", variant="primary")
            liver_output = gr.Textbox(label="Prediction")

            liver_btn.click(
                predict_liver,
                inputs=[l_age, l_gender, l_tb, l_db, l_alk, l_sgpt, l_sgot, l_proteins, l_albumin, l_ratio],
                outputs=liver_output
            )

        # =================================================
        # OBESITY
        # =================================================
        with gr.Tab("⚖️ Obesity Level"):
            gr.Markdown("## Obesity Category Prediction")
            with gr.Row():
                o_gender = gr.Dropdown(["Female", "Male"], value="Male", label="Gender")
                o_age = gr.Number(label="Age", value=21)
                o_height = gr.Number(label="Height (in meters, e.g. 1.70)", value=1.70)
                o_weight = gr.Number(label="Weight (in kg)", value=70)

            with gr.Row():
                o_family = gr.Dropdown(["No", "Yes"], value="Yes", label="Family History with Overweight")
                o_favc = gr.Dropdown(["No", "Yes"], value="Yes", label="Frequent High Caloric Food")
                o_fcvc = gr.Number(label="Vegetables Consumption Frequency (1-3)", value=2)
                o_ncp = gr.Number(label="Main Meals Frequency (1-4)", value=3)

            with gr.Row():
                o_caec = gr.Dropdown(["No", "Sometimes", "Frequently", "Always"], value="Sometimes", label="Food Between Meals")
                o_smoke = gr.Dropdown(["No", "Yes"], value="No", label="Smoker")
                o_ch2o = gr.Number(label="Daily Water Consumption (1-3)", value=2)
                o_scc = gr.Dropdown(["No", "Yes"], value="No", label="Calories Monitoring")

            with gr.Row():
                o_faf = gr.Number(label="Physical Activity Frequency (0-3)", value=1)
                o_tue = gr.Number(label="Technology Devices Usage (0-2)", value=1)
                o_calc = gr.Dropdown(["No", "Sometimes", "Frequently", "Always"], value="Sometimes", label="Alcohol Consumption")
                o_mtrans = gr.Dropdown(
                    ["Public Transportation", "Walking", "Automobile", "Motorbike", "Bike"],
                    value="Public Transportation",
                    label="Transportation Used"
                )

            obesity_btn = gr.Button("Predict Obesity Level", variant="primary")
            obesity_output = gr.Textbox(label="Prediction")

            obesity_btn.click(
                predict_obesity,
                inputs=[
                    o_gender, o_age, o_height, o_weight, o_family, o_favc, o_fcvc, o_ncp,
                    o_caec, o_smoke, o_ch2o, o_scc, o_faf, o_tue, o_calc, o_mtrans
                ],
                outputs=obesity_output
            )

import os

# Launch app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
