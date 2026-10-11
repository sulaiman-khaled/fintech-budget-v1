"""
Hussain Mjrashi
-----------------------------------------------------------------------------
University Admission Chance Predictor
NITA Academic Analytics — Predictive ML Model Deployment & Interactive Dashboard

This Streamlit app is the local/EC2/Streamlit-Cloud front end for the model
that was trained as the AWS SageMaker Canvas "Quick Build" regression
equivalent. The RandomForestRegressor below is trained at startup on
Admission_Predict_Ver1.1.csv and is tuned (n_estimators=300, max_depth=8)
to reproduce the RMSE / R^2 recorded from the Canvas "Analyze" tab.

Run locally:      streamlit run YourName_MLDeployment_App.py
Run on EC2:       nohup streamlit run YourName_MLDeployment_App.py &
Requirements:     see requirements.txt
-----------------------------------------------------------------------------
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# -----------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="Admission Chance Predictor",
    page_icon="🎓",
    layout="wide",
)

DATA_PATH = "Admission_Predict_Ver1.1.csv"


# -----------------------------------------------------------------------
# Model training (cached so it only runs once per session)
# -----------------------------------------------------------------------
@st.cache_resource
def load_data_and_train_model():
    df = pd.read_csv(DATA_PATH)
    df.columns = [c.strip() for c in df.columns]

    feature_cols = [
        "GRE Score",
        "TOEFL Score",
        "University Rating",
        "SOP",
        "LOR",
        "CGPA",
        "Research",
    ]
    X = df[feature_cols]
    y = df["Chance of Admit"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=300, max_depth=8, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = float(r2_score(y_test, preds))

    importances = pd.Series(model.feature_importances_, index=feature_cols)
    importances = importances / importances.sum()  # relative importance, sums to 1
    importances = importances.sort_values(ascending=True)  # ascending for barh plot

    dataset_avg = df[feature_cols].mean()

    return model, feature_cols, rmse, r2, importances, dataset_avg


model, feature_cols, rmse, r2, importances, dataset_avg = load_data_and_train_model()


# -----------------------------------------------------------------------
# Sidebar — Applicant Profile inputs
# -----------------------------------------------------------------------
st.sidebar.header("Applicant Profile")

gre_score = st.sidebar.slider("GRE Score", min_value=260, max_value=340, value=316)
toefl_score = st.sidebar.slider("TOEFL Score", min_value=90, max_value=120, value=107)
university_rating = st.sidebar.selectbox(
    "University Rating", options=[1, 2, 3, 4, 5], index=2
)
sop = st.sidebar.slider("SOP Strength", min_value=1.0, max_value=5.0, value=3.5, step=0.5)
lor = st.sidebar.slider("LOR Strength", min_value=1.0, max_value=5.0, value=3.5, step=0.5)
cgpa = st.sidebar.slider("CGPA", min_value=6.0, max_value=10.0, value=8.9, step=0.01)
research = st.sidebar.radio("Research Experience", options=["No", "Yes"], index=1)
research_val = 1 if research == "Yes" else 0

input_row = pd.DataFrame(
    [[gre_score, toefl_score, university_rating, sop, lor, cgpa, research_val]],
    columns=feature_cols,
)

# -----------------------------------------------------------------------
# Main panel — header + metrics
# -----------------------------------------------------------------------
st.title("🎓 University Admission Chance Predictor")
st.caption(
    "Interactive dashboard hosted via Streamlit — trained locally with parameters "
    "equivalent to the AWS SageMaker Canvas Quick Build regression model."
)

col1, col2 = st.columns(2)
col1.metric("Model RMSE", f"{rmse:.4f}")
col2.metric("Model R²", f"{r2:.4f}")

# -----------------------------------------------------------------------
# Prediction
# -----------------------------------------------------------------------
predicted_chance = float(model.predict(input_row)[0])
predicted_chance = min(max(predicted_chance, 0.0), 1.0)

st.subheader("Predicted Chance of Admit")
st.progress(predicted_chance)
st.markdown(f"### {predicted_chance * 100:.2f}%")

# -----------------------------------------------------------------------
# Charts — feature importance & profile vs. dataset average
# -----------------------------------------------------------------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Feature Importance (Column Impact)")
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    ax1.barh(importances.index, importances.values, color="#4C72B0")
    ax1.set_xlabel("Relative Importance")
    st.pyplot(fig1)

with chart_col2:
    st.subheader("Your Profile vs. Dataset Average")
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    x = np.arange(len(feature_cols))
    width = 0.35
    ax2.bar(x - width / 2, [dataset_avg[c] for c in feature_cols], width, label="Dataset avg")
    ax2.bar(x + width / 2, [input_row.iloc[0][c] for c in feature_cols], width, label="Your profile")
    ax2.set_xticks(x)
    ax2.set_xticklabels(feature_cols, rotation=45, ha="right")
    ax2.legend()
    st.pyplot(fig2)

# -----------------------------------------------------------------------
# Footer — deployment architecture note
# -----------------------------------------------------------------------
st.markdown("---")
st.caption(
    "Deployment architecture: PyCharm/Streamlit (Week 14) → GitHub 'nita20' (Week 15) "
    "→ AWS EC2 + Apache2 reverse-proxy on port 80, and Streamlit Cloud hybrid deploy (Week 16)."
)
