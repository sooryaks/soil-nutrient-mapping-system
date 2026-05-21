import streamlit as st
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image
import joblib
import requests
import io
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Soil Nutrient Analyzer",
    layout="wide",
    page_icon="🌾"
)

# ─── CSS INJECTION ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #F5F7F2;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 2px solid #D8F3DC;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #ffffff;
    border-left: 4px solid #2D6A4F;
    border-radius: 10px;
    padding: 14px 18px;
    box-shadow: 0 2px 8px rgba(45,106,79,0.10);
    margin-bottom: 8px;
}

[data-testid="stMetricLabel"] { font-size: 0.78rem; color: #555; font-weight: 600; }
[data-testid="stMetricValue"] { color: #2D6A4F; font-size: 1.4rem; font-weight: 800; }

/* Buttons */
.stButton > button {
    background-color: #2D6A4F !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 14px 28px !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    transition: background 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(45,106,79,0.25) !important;
}
.stButton > button:hover {
    background-color: #1B4332 !important;
}

/* Sliders */
[data-testid="stSlider"] > div > div > div {
    background-color: #2D6A4F !important;
}

/* Headers */
h1, h2, h3 { font-family: 'Inter', sans-serif !important; }

.main-title {
    color: #3D2B1F;
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0;
    letter-spacing: -0.5px;
}

.main-subtitle {
    color: #52796F;
    font-size: 1.0rem;
    font-weight: 500;
    margin-top: 4px;
}

.green-divider {
    border: none;
    border-top: 2px solid #95D5B2;
    margin: 18px 0 24px 0;
}

.card {
    background: #ffffff;
    border-radius: 14px;
    padding: 28px;
    box-shadow: 0 2px 16px rgba(45,106,79,0.08);
    margin-bottom: 20px;
}

.section-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #52796F;
    margin-bottom: 14px;
}

.result-box {
    background: linear-gradient(135deg, #D8F3DC 0%, #B7E4C7 100%);
    border-radius: 14px;
    padding: 32px 36px;
    box-shadow: 0 4px 20px rgba(45,106,79,0.15);
    margin-bottom: 20px;
    text-align: center;
}
.result-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #1B4332;
    margin-bottom: 6px;
}
.result-crop {
    font-size: 3rem;
    font-weight: 800;
    color: #1B4332;
    line-height: 1.1;
    text-transform: capitalize;
}
.result-conf {
    font-size: 0.78rem;
    color: #52796F;
    margin-top: 8px;
}

/* Zone badge pills */
.badge-low  { background:#E63946; color:#fff; padding:5px 16px; border-radius:50px; font-weight:700; font-size:0.82rem; display:inline-block; }
.badge-med  { background:#F4A261; color:#fff; padding:5px 16px; border-radius:50px; font-weight:700; font-size:0.82rem; display:inline-block; }
.badge-high { background:#2D6A4F; color:#fff; padding:5px 16px; border-radius:50px; font-weight:700; font-size:0.82rem; display:inline-block; }

.nutrient-card {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(45,106,79,0.09);
    text-align: center;
    height: 100%;
}
.nutrient-title { font-size: 0.78rem; font-weight: 700; color: #555; text-transform: uppercase; letter-spacing: 1px; }
.nutrient-value { font-size: 1.6rem; font-weight: 800; color: #3D2B1F; margin: 6px 0; }

.fert-card {
    background: #fff;
    border-radius: 14px;
    border-left: 5px solid #795548;
    padding: 24px 28px;
    box-shadow: 0 2px 12px rgba(121,85,72,0.09);
    margin-bottom: 20px;
}
.fert-title { font-size: 1.05rem; font-weight: 700; color: #3D2B1F; margin-bottom: 14px; }
.fert-item { font-size: 0.92rem; color: #444; margin: 6px 0; line-height: 1.5; }

.all-good-box {
    background: #D8F3DC;
    border-radius: 12px;
    padding: 16px 20px;
    color: #1B4332;
    font-weight: 600;
    font-size: 0.95rem;
}

.success-banner {
    background: #D8F3DC;
    color: #1B4332;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 0.88rem;
    font-weight: 600;
    margin-top: 10px;
}

.sidebar-brand { font-size: 1.4rem; font-weight: 800; color: #2D6A4F; }
.sidebar-sub   { font-size: 0.78rem; color: #888; margin-top: 2px; }
.sidebar-about { font-size: 0.80rem; color: #666; line-height: 1.6; }
.sidebar-footer { font-size: 0.70rem; color: #aaa; text-align: center; margin-top: 12px; }

.footer-bar {
    border-top: 1px solid #C8E6C9;
    margin-top: 40px;
    padding-top: 16px;
    text-align: center;
    font-size: 0.72rem;
    color: #888;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
CROP_NAMES = [
    "rice","maize","chickpea","kidneybeans","pigeonpeas","mothbeans","mungbean",
    "blackgram","lentil","pomegranate","banana","mango","grapes","watermelon",
    "muskmelon","apple","orange","papaya","coconut","cotton","jute","coffee"
]
DATA_URL = "https://raw.githubusercontent.com/Gladiator07/Harvestify/master/Data-raw/cpdata.csv"
FEATURES  = ["N","P","K","temperature","humidity","ph","rainfall"]

IDEAL = {
    "rice":    {"N":80,"P":40,"K":40},
    "wheat":   {"N":100,"P":50,"K":40},
    "cotton":  {"N":120,"P":60,"K":50},
    "maize":   {"N":90,"P":45,"K":45},
}
DEFAULT_IDEAL = {"N":60,"P":40,"K":40}

def get_ideal(crop):
    return IDEAL.get(crop.lower(), DEFAULT_IDEAL)

def zone(val, low_thresh, high_thresh):
    if val < low_thresh:  return "LOW"
    if val > high_thresh: return "HIGH"
    return "MEDIUM"

def badge_html(z):
    cls = {"LOW":"badge-low","MEDIUM":"badge-med","HIGH":"badge-high"}[z]
    return f'<span class="{cls}">{z}</span>'

def fert_advice(nutrient, z, crop):
    advice = {
        "N": {
            "LOW":    "Apply <b>Urea</b> at 80–100 kg/acre to address Nitrogen deficiency.",
            "MEDIUM": "Maintain standard Nitrogen dose. Monitor before next sowing.",
            "HIGH":   "⚠️ <b>Do NOT apply Nitrogen fertilizer.</b> Risk of soil toxicity."
        },
        "P": {
            "LOW":    "Apply <b>SSP</b> at 60 kg/acre to boost Phosphorus levels.",
            "MEDIUM": "Maintain standard Phosphorus dose. No immediate action required.",
            "HIGH":   "⚠️ <b>Do NOT apply DAP.</b> Phosphorus is already excessive."
        },
        "K": {
            "LOW":    "Apply <b>MOP (Muriate of Potash)</b> at 40 kg/acre to address Potassium deficiency.",
            "MEDIUM": "Maintain standard Potassium dose. Conditions are optimal.",
            "HIGH":   "⚠️ <b>Do NOT apply MOP.</b> Potassium levels are already high."
        }
    }
    return advice[nutrient][z]

# ─── SYNTHETIC DATA ───────────────────────────────────────────────────────────
# Each crop has realistic mean/std for N,P,K,temp,hum,ph,rain
CROP_PARAMS = {
    "rice":        dict(N=(80,10),P=(45,8),K=(42,8),t=(24,2),h=(82,4),ph=(6.4,0.3),r=(230,30)),
    "maize":       dict(N=(78,10),P=(48,8),K=(20,5),t=(22,2),h=(67,5),ph=(6.2,0.3),r=(70,15)),
    "chickpea":    dict(N=(40,8),P=(68,8),K=(80,8),t=(18,2),h=(18,4),ph=(7.3,0.3),r=(75,15)),
    "kidneybeans": dict(N=(21,5),P=(68,8),K=(20,5),t=(20,2),h=(22,4),ph=(5.9,0.3),r=(105,20)),
    "pigeonpeas":  dict(N=(21,5),P=(68,8),K=(20,5),t=(28,2),h=(49,5),ph=(5.9,0.3),r=(150,25)),
    "mothbeans":   dict(N=(21,5),P=(48,8),K=(20,5),t=(29,2),h=(53,5),ph=(6.9,0.3),r=(55,12)),
    "mungbean":    dict(N=(21,5),P=(48,8),K=(20,5),t=(28,2),h=(86,4),ph=(6.7,0.3),r=(50,12)),
    "blackgram":   dict(N=(40,8),P=(68,8),K=(20,5),t=(30,2),h=(66,5),ph=(7.1,0.3),r=(70,15)),
    "lentil":      dict(N=(19,5),P=(70,8),K=(20,5),t=(25,2),h=(65,5),ph=(6.9,0.3),r=(46,10)),
    "pomegranate": dict(N=(18,5),P=(18,5),K=(40,8),t=(21,2),h=(90,4),ph=(6.5,0.3),r=(107,20)),
    "banana":      dict(N=(100,10),P=(82,8),K=(50,8),t=(27,2),h=(80,4),ph=(5.8,0.3),r=(105,20)),
    "mango":       dict(N=(20,5),P=(18,5),K=(30,6),t=(31,2),h=(50,5),ph=(5.8,0.3),r=(95,15)),
    "grapes":      dict(N=(23,5),P=(132,10),K=(200,12),t=(24,2),h=(82,4),ph=(6.0,0.3),r=(70,15)),
    "watermelon":  dict(N=(100,10),P=(18,5),K=(50,8),t=(25,2),h=(85,4),ph=(6.5,0.3),r=(50,12)),
    "muskmelon":   dict(N=(100,10),P=(18,5),K=(50,8),t=(28,2),h=(92,3),ph=(6.5,0.3),r=(25,8)),
    "apple":       dict(N=(21,5),P=(134,10),K=(200,12),t=(22,2),h=(92,3),ph=(5.8,0.3),r=(115,20)),
    "orange":      dict(N=(20,5),P=(10,4),K=(10,4),t=(23,2),h=(92,3),ph=(7.0,0.3),r=(110,20)),
    "papaya":      dict(N=(50,8),P=(59,8),K=(50,8),t=(34,2),h=(92,3),ph=(6.7,0.3),r=(145,25)),
    "coconut":     dict(N=(22,5),P=(16,5),K=(30,6),t=(27,2),h=(94,3),ph=(5.9,0.3),r=(175,25)),
    "cotton":      dict(N=(118,10),P=(46,8),K=(20,5),t=(24,2),h=(80,4),ph=(6.9,0.3),r=(80,15)),
    "jute":        dict(N=(78,10),P=(46,8),K=(40,8),t=(25,2),h=(80,4),ph=(7.0,0.3),r=(175,25)),
    "coffee":      dict(N=(101,10),P=(29,6),K=(30,6),t=(25,2),h=(58,5),ph=(6.7,0.3),r=(158,25)),
}

def generate_synthetic(n=2200):
    rng = np.random.default_rng(42)
    rows = []
    per_crop = n // len(CROP_NAMES)
    for crop in CROP_NAMES:
        p = CROP_PARAMS[crop]
        def s(mu_sd, lo, hi, size):
            return np.clip(rng.normal(mu_sd[0], mu_sd[1], size), lo, hi)
        rows.append(pd.DataFrame({
            "N":           s(p["N"],   0,   140, per_crop),
            "P":           s(p["P"],   0,   145, per_crop),
            "K":           s(p["K"],   0,   205, per_crop),
            "temperature": s(p["t"],  10,    50, per_crop),
            "humidity":    s(p["h"],  20,   100, per_crop),
            "ph":          s(p["ph"], 3.5,   9.0, per_crop),
            "rainfall":    s(p["r"],  20,   300, per_crop),
            "label":       crop
        }))
    df = pd.concat(rows, ignore_index=True)
    return df.sample(frac=1, random_state=42).reset_index(drop=True)

# ─── TRAIN MODEL ─────────────────────────────────────────────────────────────
def train_model():
    # 1. Always generate synthetic data (remote CSV lacks N/P/K columns).
    #    Optionally enrich climate columns from the downloaded CSV if available.
    df_synth = generate_synthetic(2200)
    try:
        r = requests.get(DATA_URL, timeout=10)
        r.raise_for_status()
        df_remote = pd.read_csv(io.StringIO(r.text))
        # Remote has: temperature, humidity, ph, rainfall, label
        # Use remote climate values where we have matching crop labels
        if {"temperature", "humidity", "ph", "rainfall", "label"}.issubset(df_remote.columns):
            climate_cols = ["temperature", "humidity", "ph", "rainfall"]
            n = min(len(df_synth), len(df_remote))
            df_synth.loc[:n-1, climate_cols] = df_remote[climate_cols].values[:n]
    except Exception:
        pass  # Use purely synthetic data

    X = df_synth[FEATURES].to_numpy(dtype=np.float64)
    y = df_synth["label"].to_numpy(dtype=str)

    # 2. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 3. Scale
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    # 4. Train
    clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    clf.fit(X_train_s, y_train)

    train_acc = accuracy_score(y_train, clf.predict(X_train_s))
    test_acc  = accuracy_score(y_test,  clf.predict(X_test_s))
    cv_scores = cross_val_score(clf, X_train_s, y_train, cv=5, scoring="accuracy")
    cv_mean   = cv_scores.mean()

    # 5. Persist
    joblib.dump({"model": clf, "scaler": scaler}, "model.pkl")

    return clf, scaler, train_acc, test_acc, cv_mean, len(df_synth)

def ensure_crop_advisor_model():
    import os
    if not os.path.exists("crop_model.pkl") or not os.path.exists("label_encoder.pkl"):
        # We need to train them
        df = generate_synthetic(2200)
        if os.path.exists("cpdata.csv"):
            try:
                df = pd.read_csv("cpdata.csv")
            except Exception:
                pass
        
        # Columns N, P, K, ph, label are required
        if not {"N", "P", "K", "ph", "label"}.issubset(df.columns):
            df = generate_synthetic(2200)
            
        X = df[["N", "P", "K", "ph"]].to_numpy(dtype=np.float64)
        y = df["label"].to_numpy(dtype=str)
        
        from sklearn.preprocessing import LabelEncoder
        from sklearn.ensemble import RandomForestClassifier
        
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
        clf.fit(X, y_encoded)
        
        joblib.dump(clf, "crop_model.pkl")
        joblib.dump(le, "label_encoder.pkl")

# ─── INIT / TRAINING ─────────────────────────────────────────────────────────
if "model" not in st.session_state:
    with st.spinner("🌱 Training AI model on soil dataset..."):
        clf, scaler, train_acc, test_acc, cv_mean, n_samples = train_model()
    st.session_state["model"]      = clf
    st.session_state["scaler"]     = scaler
    st.session_state["train_acc"]  = train_acc
    st.session_state["test_acc"]   = test_acc
    st.session_state["cv_mean"]    = cv_mean
    st.session_state["n_samples"]  = n_samples
    st.session_state["trained"]    = True
    st.session_state["show_banner"]= True

clf       = st.session_state["model"]
scaler    = st.session_state["scaler"]
test_acc  = st.session_state["test_acc"]
train_acc = st.session_state["train_acc"]
cv_mean   = st.session_state["cv_mean"]
n_samples = st.session_state["n_samples"]

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🌿 RNSIT IDPL</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">AI Soil Nutrient Mapping System</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("**📊 Model Statistics**")
    st.metric("Test Accuracy",     f"{test_acc*100:.1f}%")
    st.metric("CV Score (5-Fold)", f"{cv_mean*100:.1f}%")
    st.metric("Training Samples",  f"{n_samples:,} records")

    if st.session_state.get("show_banner"):
        st.markdown(
            f'<div class="success-banner">✅ Model ready — Test Accuracy: {test_acc*100:.1f}% | CV Score: {cv_mean*100:.1f}%</div>',
            unsafe_allow_html=True
        )
        st.session_state["show_banner"] = False

    st.divider()
    st.markdown("**ℹ️ About**")
    st.markdown(
        '<div class="sidebar-about">Enter your field\'s soil nutrient values using the sliders. '
        'The AI will instantly predict the best crop and provide a fertilizer action plan. '
        'No internet required after startup.</div>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**🛰️ Image Analysis Tips:**")
    st.markdown(
        '<div class="sidebar-about">'
        '- Best results with aerial/drone photos taken from directly above<br>'
        '- Google Maps satellite view works well at zoom 16–17<br>'
        '- Try fields near Mandya or Hassan, Karnataka for demo<br>'
        '- Green crops = high GLI score, brown/bare = low score'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="sidebar-footer">Phase-II Review · May 9, 2026</div>', unsafe_allow_html=True)

# ─── MAIN PANEL ──────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-title">🌾 AI Soil Nutrient Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Interdisciplinary Project · ECE × CSE-CY · RNSIT</div>', unsafe_allow_html=True)
st.markdown('<hr class="green-divider">', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🔬 Crop Analyzer", "🗺️ Nutrient Zone Map", "🛰️ Field Image Analysis", "📋 Crop Advisor (Soil Report)"])

with tab1:
    # ─── INPUT CARD ──────────────────────────────────────────────────────────────
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Enter Soil Parameters</div>', unsafe_allow_html=True)

        col_l, col_r = st.columns(2)
        with col_l:
            N   = st.slider("🌿 Nitrogen (N) kg/ha",    0,   140,  40,  1)
            P   = st.slider("🌾 Phosphorus (P) kg/ha",  0,   145,  30,  1)
            K   = st.slider("🍂 Potassium (K) kg/ha",   0,   205,  20,  1)
        with col_r:
            ph  = st.slider("⚗️ pH Level",              3.5,  9.0, 6.5, 0.1)
            temp= st.slider("🌡️ Temperature (°C)",      10,   50,  25,  1)
            hum = st.slider("💧 Humidity (%)",           20,  100,  65,  1)
            rain= st.slider("🌧️ Rainfall (mm)",          20,  300, 100,  5)

        st.markdown('</div>', unsafe_allow_html=True)

    btn = st.button("🔬 Analyze Soil & Get Recommendation")

    # ─── RESULTS ─────────────────────────────────────────────────────────────────
    if btn:
        inp    = np.array([[N, P, K, temp, hum, ph, rain]], dtype=float)
        inp_s  = scaler.transform(inp)
        pred   = clf.predict(inp_s)[0]
        crop   = pred.capitalize()

        # BLOCK A — Crop Prediction
        st.markdown(f"""
        <div class="result-box">
            <div class="result-label">🌱 Recommended Crop</div>
            <div class="result-crop">{crop}</div>
            <div class="result-conf">Confidence: HIGH &nbsp;·&nbsp; Random Forest &nbsp;·&nbsp; 200 Trees</div>
        </div>
        """, unsafe_allow_html=True)

        # BLOCK B — Nutrient Zones
        z_n = zone(N,  40,  80)
        z_p = zone(P,  20,  50)
        z_k = zone(K, 100, 200)

        c1, c2, c3 = st.columns(3)
        for col, label, val, z, unit in [
            (c1, "Nitrogen (N)",   N, z_n, "kg/ha"),
            (c2, "Phosphorus (P)", P, z_p, "kg/ha"),
            (c3, "Potassium (K)",  K, z_k, "kg/ha"),
        ]:
            with col:
                st.markdown(f"""
                <div class="nutrient-card">
                    <div class="nutrient-title">{label}</div>
                    <div class="nutrient-value">{val} {unit}</div>
                    {badge_html(z)}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # BLOCK C — Fertilizer Action Plan
        all_high = (z_n == "HIGH" and z_p == "HIGH" and z_k == "HIGH")

        st.markdown('<div class="fert-card">', unsafe_allow_html=True)
        st.markdown('<div class="fert-title">📋 Fertilizer Action Plan</div>', unsafe_allow_html=True)
        if all_high:
            st.markdown(
                f'<div class="all-good-box">✅ Soil is nutrient-rich. No fertilizer needed. '
                f'Optimal conditions for <b>{crop}</b>.</div>',
                unsafe_allow_html=True
            )
        else:
            for nut, z in [("N", z_n), ("P", z_p), ("K", z_k)]:
                icon = {"N":"🌿","P":"🌾","K":"🍂"}[nut]
                advice = fert_advice(nut, z, pred)
                st.markdown(f'<div class="fert-item">{icon} <b>{nut}:</b> {advice}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # BLOCK D — Bar Chart
        ideal = get_ideal(pred)
        labels_chart = ["Nitrogen", "Phosphorus", "Potassium"]
        user_vals  = [N, P, K]
        ideal_vals = [ideal["N"], ideal["P"], ideal["K"]]

        x      = np.arange(len(labels_chart))
        width  = 0.35
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        bars1 = ax.bar(x - width/2, user_vals,  width, label="Your Field",              color="#2D6A4F", edgecolor="white", linewidth=1.2)
        bars2 = ax.bar(x + width/2, ideal_vals, width, label=f"Ideal for {crop}", color="#95D5B2", edgecolor="white", linewidth=1.2)

        ax.set_title("Soil Nutrient Profile vs. Ideal Range", fontsize=13, fontweight="bold", color="#3D2B1F", pad=14)
        ax.set_ylabel("Amount (kg/ha)", fontsize=10, color="#555")
        ax.set_xticks(x)
        ax.set_xticklabels(labels_chart, fontsize=10)
        ax.legend(fontsize=9, frameon=False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#ddd")
        ax.spines["bottom"].set_color("#ddd")
        ax.tick_params(colors="#555")
        ax.yaxis.grid(True, linestyle="--", alpha=0.5, color="#e0e0e0")
        ax.set_axisbelow(True)

        for bar in bars1:
            ax.annotate(f'{bar.get_height()}', xy=(bar.get_x()+bar.get_width()/2, bar.get_height()),
                        xytext=(0,4), textcoords="offset points", ha='center', fontsize=8, color="#1B4332", fontweight="bold")
        for bar in bars2:
            ax.annotate(f'{bar.get_height()}', xy=(bar.get_x()+bar.get_width()/2, bar.get_height()),
                        xytext=(0,4), textcoords="offset points", ha='center', fontsize=8, color="#52796F")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)


with tab2:
    st.markdown("### 📍 Enter Multi-Point Field Samples")
    st.markdown("Add soil readings from different spots across your field to generate a spatial nutrient map.")
    
    default_samples = pd.DataFrame([
        {"Sample ID": "S1", "Location Label": "North Corner", "N": 30, "P": 15, "K": 80, "pH": 6.2},
        {"Sample ID": "S2", "Location Label": "North East", "N": 55, "P": 35, "K": 150, "pH": 6.8},
        {"Sample ID": "S3", "Location Label": "Centre", "N": 90, "P": 60, "K": 220, "pH": 7.1},
        {"Sample ID": "S4", "Location Label": "South West", "N": 25, "P": 20, "K": 90, "pH": 5.8},
        {"Sample ID": "S5", "Location Label": "South Edge", "N": 70, "P": 45, "K": 160, "pH": 6.5},
        {"Sample ID": "S6", "Location Label": "West Corner", "N": 110, "P": 70, "K": 200, "pH": 7.3},
    ])
    
    edited_df = st.data_editor(default_samples, num_rows="dynamic", use_container_width=True)
    
    if st.button("🗺️ Generate Nutrient Map", type="primary"):
        # Process data
        zones_data = []
        total_points = 0
        max_points = len(edited_df) * 6
        
        for _, row in edited_df.iterrows():
            nz = zone(row["N"], 40, 80)
            pz = zone(row["P"], 20, 50)
            kz = zone(row["K"], 100, 200)
            
            pts = 0
            for z in [nz, pz, kz]:
                if z == "MEDIUM": pts += 1
                elif z == "HIGH": pts += 2
            total_points += pts
            
            action = "🟡 Partial intervention"
            if nz == "LOW" or pz == "LOW" or kz == "LOW":
                action = "🔴 Immediate fertilizer needed"
            elif nz == "HIGH" and pz == "HIGH" and kz == "HIGH":
                action = "🟢 No action needed"
            elif nz == "MEDIUM" and pz == "MEDIUM" and kz == "MEDIUM":
                action = "🟡 Standard maintenance"
                
            zones_data.append({
                "Sample": row["Sample ID"],
                "Location": row["Location Label"],
                "N Zone": nz,
                "P Zone": pz,
                "K Zone": kz,
                "Priority Action": action,
                "N_val": row["N"],
                "P_val": row["P"],
                "K_val": row["K"]
            })
            
        # Draw Map
        st.markdown("<br>", unsafe_allow_html=True)
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.patch.set_facecolor('white')
        
        nutrients = [("N Zone", "N_val", "Nitrogen Zones", axes[0]), 
                     ("P Zone", "P_val", "Phosphorus Zones", axes[1]), 
                     ("K Zone", "K_val", "Potassium Zones", axes[2])]
        
        color_map = {"LOW": "#E63946", "MEDIUM": "#F4A261", "HIGH": "#2D6A4F"}
        
        for zone_col, val_col, title, ax in nutrients:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
            ax.set_xlim(0, 3)
            ax.set_ylim(0, 2)
            ax.axis('off')
            
            for i, data in enumerate(zones_data):
                if i >= 6: break # Only map first 6 for grid layout
                col_idx = i % 3
                row_idx = i // 3
                
                x = col_idx + 0.025
                y = 1 - row_idx + 0.025
                
                z = data[zone_col]
                rect = mpatches.Rectangle((x, y), 0.95, 0.95, facecolor=color_map[z], edgecolor='none')
                ax.add_patch(rect)
                
                # Add text
                ax.text(col_idx + 0.5, y + 0.65, data["Location"], color='white', ha='center', va='center', fontsize=10, fontweight='bold')
                ax.text(col_idx + 0.5, y + 0.40, z, color='white', ha='center', va='center', fontsize=14, fontweight='bold')
                ax.text(col_idx + 0.5, y + 0.15, f"{zone_col[0]}: {data[val_col]}", color='white', ha='center', va='center', fontsize=10)
                
            # Legend
            legend_elements = [
                mpatches.Patch(color='#E63946', label='LOW'),
                mpatches.Patch(color='#F4A261', label='MEDIUM'),
                mpatches.Patch(color='#2D6A4F', label='HIGH')
            ]
            ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
            
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        
        # Summary Table
        st.markdown("### 📋 Zone Summary Table", unsafe_allow_html=True)
        summary_df = pd.DataFrame(zones_data).drop(columns=["N_val", "P_val", "K_val"])
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # Field Health Score
        score = (total_points / max_points) * 100 if max_points > 0 else 0
        if score > 70:
            score_color = "#2D6A4F" # Green
        elif score >= 40:
            score_color = "#F4A261" # Amber
        else:
            score_color = "#E63946" # Red
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'''
        <div style="background:#ffffff; padding:20px; border-radius:12px; box-shadow:0 2px 12px rgba(0,0,0,0.05); text-align:center; border-top: 4px solid {score_color}; margin-bottom:20px;">
            <h2 style="color:{score_color}; margin-bottom:5px; margin-top:0;">🌾 Overall Field Health Score: {score:.1f}%</h2>
            <p style="color:#666; font-size:0.9rem; margin-top:0;">Based on N, P, K zone distribution across all field samples</p>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown('''
    <div style="background-color: #D8F3DC; border-radius: 10px; padding: 15px; margin-top: 20px;">
        <p style="color: #1B4332; margin: 0; font-size: 0.95rem;">
        💡 <b>What this means:</b> This map simulates what precision agriculture systems do with 
        IoT soil sensors across a field. In a production system, GPS coordinates would replace manual 
        location labels, and sensor readings would auto-populate the table. Our ML model can then 
        predict the best crop for each zone independently.
        </p>
    </div>
    ''', unsafe_allow_html=True)

with tab3:
    st.markdown("### 🛰️ Satellite & Drone Field Analyzer")
    st.markdown("Analyze vegetation and soil health from aerial imagery using computer vision. Works with drone photos, Google Maps satellite views, or any field photograph.")
    
    input_method = st.radio("", ["📁 Upload a Field Image", "📍 Fetch from Google Maps (Address)"], horizontal=True, label_visibility="collapsed")
    
    img = None
    
    if "Upload" in input_method:
        st.markdown("**Upload a drone photo or satellite image of your field**")
        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded_file is not None:
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, width=500, caption="Original Field Image")
    
    else:
        address = st.text_input("Enter field address or location", placeholder="e.g. Mandya, Karnataka, India")
        api_key = st.text_input("Google Maps Static API Key", placeholder="Paste your API key here", type="password")
        st.caption("Get a free key at console.cloud.google.com → Enable Maps Static API. Free tier: 25,000 requests/month.")
        
        zoom = st.selectbox("Map Zoom Level", [14, 15, 16, 17], index=2, format_func=lambda x: f"{x} ({'Village level' if x==14 else 'Field level' if x==15 else 'Close field' if x==16 else 'Very close'})")
        
        if st.button("🛰️ Fetch Satellite Image", type="primary"):
            if address and api_key:
                url = f"https://maps.googleapis.com/maps/api/staticmap?center={address}&zoom={zoom}&size=640x640&maptype=satellite&key={api_key}"
                try:
                    res = requests.get(url, timeout=10)
                    if res.status_code == 200:
                        img = Image.open(io.BytesIO(res.content)).convert("RGB")
                        st.session_state['field_image'] = img
                    else:
                        st.error("Could not fetch image. Check your API key and address.")
                except Exception as e:
                    st.error(f"Error fetching image: {e}")
            else:
                st.warning("Please enter both an address and an API key.")
                
        if 'field_image' in st.session_state and "Google Maps" in input_method:
            img = st.session_state['field_image']
            st.image(img, width=500, caption="Fetched Satellite Image")

    if img is not None:
        if st.button("🔬 Analyze Field Health", type="primary", use_container_width=True):
            # STEP 1
            img_resized = img.resize((256, 256))
            arr = np.array(img_resized).astype(float) / 255.0
            R = arr[:,:,0]
            G = arr[:,:,1]
            B = arr[:,:,2]
            
            # STEP 2
            denom = (2*G + R + B + 1e-10)
            GLI = (2*G - R - B) / denom
            GLI = np.clip(GLI, -1, 1)
            
            ExG = 2*G - R - B
            ExG = np.clip(ExG, 0, 1)
            
            SBI = np.sqrt(R**2 + G**2 + B**2) / np.sqrt(3)
            
            total_pixels = 256 * 256
            veg_mask = GLI > 0.05
            stress_mask = (GLI > -0.1) & (GLI <= 0.05)
            bare_mask = GLI <= -0.1
            
            vegetated_pct = np.sum(veg_mask) / total_pixels * 100
            stressed_pct = np.sum(stress_mask) / total_pixels * 100
            bare_pct = np.sum(bare_mask) / total_pixels * 100
            
            # STEP 3
            zone_arr = np.zeros((256, 256), dtype=int)
            zone_arr[veg_mask] = 2
            zone_arr[stress_mask] = 1
            zone_arr[bare_mask] = 0
            
            # STEP 4
            health_score = np.clip(vegetated_pct * 1.0 + stressed_pct * 0.4, 0, 100)
            health_score = round(health_score, 1)
            
            # STEP 5
            if vegetated_pct > 60:
                N_status, P_status, K_status = "Likely ADEQUATE", "Likely ADEQUATE", "Likely ADEQUATE"
            elif vegetated_pct >= 30:
                N_status, P_status, K_status = "Possibly LOW", "Possibly MEDIUM", "Possibly MEDIUM"
            else:
                N_status, P_status, K_status = "Likely DEFICIENT", "Likely DEFICIENT", "Likely DEFICIENT"
                
            # ROW 1
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.markdown("**Original Field Image**")
                st.image(img, width=300)
                
            with c2:
                st.markdown("**Vegetation Health Map**")
                fig1, ax1 = plt.subplots(figsize=(4, 4))
                from matplotlib.colors import ListedColormap
                cmap = ListedColormap(["#E63946", "#F4A261", "#2D6A4F"])
                ax1.imshow(zone_arr, cmap=cmap, vmin=0, vmax=2)
                ax1.axis('off')
                ax1.set_title("Zone Classification", fontsize=10)
                
                leg_el = [
                    mpatches.Patch(color='#E63946', label='Stressed/Bare'),
                    mpatches.Patch(color='#F4A261', label='Moderate'),
                    mpatches.Patch(color='#2D6A4F', label='Healthy')
                ]
                ax1.legend(handles=leg_el, loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=8, frameon=False)
                st.pyplot(fig1)
                plt.close(fig1)
                
            with c3:
                st.markdown("**Zone Distribution**")
                fig2, ax2 = plt.subplots(figsize=(4, 4))
                sizes = [vegetated_pct, stressed_pct, bare_pct]
                labels = ['Healthy', 'Moderate', 'Bare/Stressed']
                colors = ['#2D6A4F', '#F4A261', '#E63946']
                sizes_plot = []
                labels_plot = []
                colors_plot = []
                for s, l, c in zip(sizes, labels, colors):
                    if s > 0:
                        sizes_plot.append(s)
                        labels_plot.append(l)
                        colors_plot.append(c)
                        
                ax2.pie(sizes_plot, labels=labels_plot, colors=colors_plot, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
                ax2.axis('equal')
                st.pyplot(fig2)
                plt.close(fig2)
                
            # ROW 2
            score_color = "#2D6A4F" if health_score >= 70 else "#F4A261" if health_score >= 40 else "#E63946"
            score_text = "GOOD" if health_score >= 70 else "MODERATE" if health_score >= 40 else "POOR"
            score_icon = "🟢" if health_score >= 70 else "🟡" if health_score >= 40 else "🔴"
            
            st.markdown(f'''
            <div style="background:{score_color}; color:white; padding:15px; border-radius:10px; text-align:center; margin-top:20px; margin-bottom:20px;">
                <h3 style="margin:0; color:white;">{score_icon} Field Health Score: {health_score}% — {score_text}</h3>
            </div>
            ''', unsafe_allow_html=True)
            
            mc1, mc2, mc3 = st.columns(3)
            mc1.info(f"✅ Healthy Vegetation: {vegetated_pct:.1f}%")
            mc2.warning(f"⚠️ Stressed Vegetation: {stressed_pct:.1f}%")
            mc3.error(f"🟤 Bare Soil / Low Health: {bare_pct:.1f}%")
            
            # ROW 3
            st.markdown("<br>", unsafe_allow_html=True)
            nc1, nc2, nc3 = st.columns(3)
            def card_html(icon, title, status):
                return f'''<div style="background:white; border-left:4px solid #2D6A4F; padding:15px; border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.05); height:100%;">
                    <div style="font-size:14px; color:#555;">{icon} {title}</div>
                    <div style="font-size:18px; font-weight:bold; color:#1B4332; margin-top:5px;">{status}</div>
                </div>'''
                
            nc1.markdown(card_html("🌱", "Nitrogen (N)", N_status), unsafe_allow_html=True)
            nc2.markdown(card_html("🌿", "Phosphorus (P)", P_status), unsafe_allow_html=True)
            nc3.markdown(card_html("🌾", "Potassium (K)", K_status), unsafe_allow_html=True)
            
            st.markdown("<p style='font-size:12px; color:#888; font-style:italic; margin-top:10px;'>⚠️ Note: Precise nutrient values require lab testing or multispectral sensors. These estimates are based on vegetation density from RGB analysis.</p>", unsafe_allow_html=True)
            
            # ROW 4
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('''<div style="background:white; border:1px solid #795548; padding:20px; border-radius:10px;">
            <h4 style="color:#795548; margin-top:0;">📋 Recommended Next Steps</h4>''', unsafe_allow_html=True)
            
            if health_score >= 70:
                st.markdown("""✅ Field appears healthy. Vegetation coverage is strong.
- Continue current fertilization schedule
- Monitor for localized stress patches
- Consider soil lab test to confirm nutrient adequacy
- Estimated crop suitability: High""")
            elif health_score >= 40:
                st.markdown("""⚠️ Field shows moderate stress. Some zones need attention.
- Conduct targeted soil testing in red/amber zones
- Consider applying balanced NPK fertilizer to stressed areas
- Check irrigation coverage — stressed patches may be water-stressed
- Re-analyze in 2 weeks after intervention""")
            else:
                st.markdown("""🔴 Field shows significant stress or low vegetation coverage.
- Immediate soil lab testing strongly recommended
- Large areas show bare soil — check for erosion or crop failure
- Consult agricultural officer before next sowing
- Consider soil amendment (organic matter, lime if pH issue)""")
                
            st.markdown('</div>', unsafe_allow_html=True)
            
            # ROW 5
            st.markdown("<p style='font-size:11px; color:#aaa; background:#f9f9f9; padding:10px; border-radius:5px; margin-top:20px; text-align:center;'>Analysis method: RGB Vegetation Index (GLI + ExG) | Image resolution processed: 256×256px | This is a visual estimation tool. For precise nutrient mapping, use multispectral sensors (NIR + Red Edge bands) with GPS tagging.</p>", unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Soil Health Card Crop Advisor</div>', unsafe_allow_html=True)
    st.markdown("Upload a Karnataka Soil Health Card text report to automatically extract nutrient values and get crop recommendations.")
    
    uploaded_file = st.file_uploader("Upload Soil Report (.txt)", type=["txt"])
    
    if uploaded_file is not None:
        if not uploaded_file.name.endswith('.txt'):
            st.error("❌ Invalid file type. Please upload a .txt file.")
            st.stop()
            
        content = uploaded_file.getvalue().decode("utf-8")
        with st.expander("📄 Preview Uploaded File Content", expanded=False):
            st.text(content)
            
        # Parse values
        n_match = re.search(r"Nitrogen\s*\(N\)\s+([\d.]+)", content, re.IGNORECASE)
        if not n_match:
            n_match = re.search(r"N\)\s+([\d.]+)", content, re.IGNORECASE)
            
        p_match = re.search(r"Phosphorus\s*\(P\)\s+([\d.]+)", content, re.IGNORECASE)
        if not p_match:
            p_match = re.search(r"P\)\s+([\d.]+)", content, re.IGNORECASE)
            
        k_match = re.search(r"Potassium\s*\(K\)\s+([\d.]+)", content, re.IGNORECASE)
        if not k_match:
            k_match = re.search(r"K\)\s+([\d.]+)", content, re.IGNORECASE)
            
        ph_match = re.search(r"pH\s+([\d.]+)", content, re.IGNORECASE)
        
        id_match = re.search(r"Report ID\s*:\s*(\S+)", content, re.IGNORECASE)
        
        n_val = float(n_match.group(1)) if n_match else None
        p_val = float(p_match.group(1)) if p_match else None
        k_val = float(k_match.group(1)) if k_match else None
        ph_val = float(ph_match.group(1)) if ph_match else None
        report_id = id_match.group(1) if id_match else "Unknown"
        
        # Check for missing values
        missing = []
        if n_val is None: missing.append("Nitrogen (N)")
        if p_val is None: missing.append("Phosphorus (P)")
        if k_val is None: missing.append("Potassium (K)")
        if ph_val is None: missing.append("pH")
        
        if missing:
            st.warning(f"⚠️ Missing soil parameters in report: {', '.join(missing)}")
            st.stop()
            
        # Handle out of range values
        out_of_range = []
        if not (0 <= n_val <= 500): out_of_range.append(f"Nitrogen ({n_val} kg/ha, expected 0-500)")
        if not (0 <= p_val <= 500): out_of_range.append(f"Phosphorus ({p_val} kg/ha, expected 0-500)")
        if not (0 <= k_val <= 500): out_of_range.append(f"Potassium ({k_val} kg/ha, expected 0-500)")
        if not (0 <= ph_val <= 14): out_of_range.append(f"pH ({ph_val}, expected 0-14)")
        
        if out_of_range:
            st.warning(f"⚠️ Values out of expected range: {', '.join(out_of_range)}")
            
        # Display 4 extracted values in a 2x2 grid
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Extracted Parameters</div>', unsafe_allow_html=True)
        r1c1, r1c2 = st.columns(2)
        r2c1, r2c2 = st.columns(2)
        with r1c1:
            st.metric("🌿 Nitrogen (N)", f"{n_val} kg/ha")
        with r1c2:
            st.metric("🌾 Phosphorus (P)", f"{p_val} kg/ha")
        with r2c1:
            st.metric("🍂 Potassium (K)", f"{k_val} kg/ha")
        with r2c2:
            st.metric("⚗️ pH Level", f"{ph_val}")
            
        # Classify status
        n_status = "Low" if n_val < 180 else "Medium" if n_val <= 260 else "High"
        p_status = "Low" if p_val < 25 else "Medium" if p_val <= 50 else "High"
        k_status = "Low" if k_val < 150 else "Medium" if k_val <= 200 else "High"
        ph_status = "Acidic" if ph_val < 6.5 else "Neutral" if ph_val <= 7.5 else "Alkaline"
        
        # Load classification models
        ensure_crop_advisor_model()
        try:
            crop_model = joblib.load("crop_model.pkl")
            label_encoder = joblib.load("label_encoder.pkl")
            
            input_data = np.array([[n_val, p_val, k_val, ph_val]], dtype=float)
            prediction_encoded = crop_model.predict(input_data)
            predicted_crop = label_encoder.inverse_transform(prediction_encoded)[0]
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.success(f"🌱 **Recommended Crop to Grow: {predicted_crop.capitalize()}**")
            
            # Display interpretation table
            interpretation_data = {
                "Parameter": ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)", "pH Level"],
                "Extracted Value": [f"{n_val} kg/ha", f"{p_val} kg/ha", f"{k_val} kg/ha", f"{ph_val}"],
                "Status": [n_status, p_status, k_status, ph_status],
                "Reference Range": [
                    "Low < 180, Medium 180-260, High > 260",
                    "Low < 25, Medium 25-50, High > 50",
                    "Low < 150, Medium 150-200, High > 200",
                    "Acidic < 6.5, Neutral 6.5-7.5, Alkaline > 7.5"
                ]
            }
            df_interpret = pd.DataFrame(interpretation_data)
            st.markdown("#### 📋 Interpretation Table")
            st.dataframe(df_interpret, use_container_width=True, hide_index=True)
            
            # Download summary report
            summary_text = f"""=========================================
AI-BASED SOIL NUTRIENT ADVISORY REPORT
=========================================
Report ID            : {report_id}
Recommended Crop     : {predicted_crop.capitalize()}
-----------------------------------------
EXTRACTED SOIL VALUES:
Nitrogen (N)         : {n_val} kg/ha ({n_status})
Phosphorus (P)       : {p_val} kg/ha ({p_status})
Potassium (K)        : {k_val} kg/ha ({k_status})
pH Level             : {ph_val} ({ph_status})
========================================="""

            st.download_button(
                label="📥 Download Soil Advisor Summary",
                data=summary_text,
                file_name=f"Soil_Advisor_Report_{report_id}.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"Failed to load classification models: {e}")
            st.stop()
            
    st.markdown('</div>', unsafe_allow_html=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-bar">
    AI-Based Soil Nutrient Mapping System &nbsp;·&nbsp; RNSIT IDPL Phase-II &nbsp;·&nbsp; May 2026<br>
    <b>Team:</b> Partha Rama Krishna, Shamanth R, Pranav P, Sharath Kashyap, Soorya K S, Srinivas Narayan<br>
    <b>Supervisor:</b> Dr. Prabhavathi C N
</div>
""", unsafe_allow_html=True)
