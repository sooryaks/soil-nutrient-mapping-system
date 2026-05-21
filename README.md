# AI-Based Soil Nutrient Mapping System

A Streamlit-based web application for crop recommendation, soil nutrient mapping, field image analysis (RGB vegetation/soil indexing), and soil health card report parsing.

## Features

1. **🔬 Crop Analyzer**: Single-field crop suitability predictor using a Random Forest model.
2. **🗺️ Nutrient Zone Map**: Multi-sample spatial mapping of Nitrogen (N), Phosphorus (P), and Potassium (K) with color-coded classification.
3. **🛰️ Field Image Analysis**: Drone/satellite RGB-based vegetation (ExG) and soil analysis.
4. **📋 Crop Advisor (Soil Report)**: Parses a text-based Karnataka Soil Health Card using regex, displays a metrics grid, predicts suitability, and generates a downloadable PDF/text summary.

## Setup & Running

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the App**:
   ```bash
   streamlit run app.py
   ```

*Note: The machine learning models (`model.pkl`, `crop_model.pkl`, `label_encoder.pkl`) are automatically trained and generated on startup using the provided `cpdata.csv` dataset, so there is no need to commit large model files to Git.*
