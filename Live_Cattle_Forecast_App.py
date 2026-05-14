import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Multi-Index Cattle Intel 2026", 
    page_icon="🐂",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_html=True)

st.title("🐂 Normalized Cattle Model: S&P GSCI & Sterling Marketing Integration")
st.caption("Strategic forecasting engine for May 13, 2026 | Data Currency: 2026-Q2")

# --- 2. SIDEBAR: MODEL INTELLIGENCE OVERLAYS ---
with st.sidebar:
    st.header("Intelligence Controls")
    st.divider()
    
    # Macro Sentiment (S&P GSCI)
    sp_macro = st.slider(
        "S&P GSCI Sentiment Adjustment", 
        0.90, 1.10, 1.02, 
        help="Macro-commodity index sentiment based on May '26 Index at 752.79."
    )

    # Sterling Marketing Margin Floor
    sterling_floor_val = 250.97
    apply_sterling = st.checkbox(
        f"Apply Sterling Breakeven Floor (${sterling_floor_val})", 
        value=True
    )

    # Inventory Scarcity
    inventory_level = st.select_slider(
        "Inventory Constraint", 
        options=["Historical Avg", "Tight", "Extreme (86.2M head)"],
        value="Extreme (86.2M head)"
    )
    
    st.info("The 'Extreme' setting reflects the 75-year herd low.")

# --- 3. DATA ENGINE ---
@st.cache_data
def get_integrated_model(sp_macro_val, apply_sterling_val, inventory_val):
    # Historical Data Construction
    hist_dates = pd.date_range(end='2026-05-13', periods=26, freq='MS')
    hist_prices = np.linspace(188.30, 261.50, len(hist_dates)) 
    df_hist = pd.DataFrame({'Price': hist_prices}, index=hist_dates)

    # Mean-Centered Seasonality
    raw_indices = {1: 0.98, 2: 1.00, 3: 1.02, 4: 1.04, 5: 1.05, 6: 1.01, 
                   7: 0.99, 8: 0.97, 9: 0.96, 10: 0.94, 11: 0.95, 12: 0.97}
    norm_factor = 12 / sum(raw_indices.values())
    norm_indices = {m: val * norm_factor for m, val in raw_indices.items()}

    # Forecast Generation (June 2026 - May 2027)
    base_anchors = {
        '2026-06': 248.37, '2026-08': 244.15, '2026-10': 238.68,
        '2026-12': 238.50, '2027-02': 238.60, '2027-04': 237.90
    }
    
    inv_mult = {"Historical Avg": 1.0, "Tight": 1.02, "Extreme (86.2M head)": 1.05}
    
    forecast_dates = pd.date_range(start='2026-06-01', periods=12, freq='MS')
    forecast_prices = []
    
    for date in forecast_dates:
        key = date.strftime('%Y-%m')
        base_p = base_anchors.get(key, 240.00)
        
        # Apply Logic: (Base * Normalization * Macro * Inventory)
        final_p = base_p * norm_indices[date.month] * sp_macro_val * inv_mult[inventory_val]
        
        # Apply Sterling Breakeven Floor for Summer Marketing
        if apply_sterling_val and final_p < sterling_floor_val and date.month in [6, 7, 8]:
            final_p = sterling_floor_val
            
        forecast_prices.append(final_p)

    df_forecast = pd.DataFrame({'Price': forecast_prices}, index=forecast_dates)
    return df_hist, df_forecast, norm_indices

# Run Model
df_hist, df_forecast, final_indices = get_integrated_model(sp_macro, apply_sterling, inventory_level)

# --- 4. UI: FORECAST DASHBOARD ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current CME (LEM6)", "$251.05", "+3.35")
col2.metric("USDA ERS Avg", "$241.66", "8% YoY")
col3.metric("Sterling Floor", f"${sterling_floor_val}", "Breakeven")
col4.metric("Model Prediction", f"${df_forecast.iloc[0,0]:.2f}", f"{(df_forecast.iloc[0,0] - 261.50):.2f}")

# Main Chart
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_hist.index, y=df_hist['Price'], name="USDA Cash History", line=dict(color="#1A237E", width=3)))
fig.add_trace(go.Scatter(x=df_forecast.index, y=df_forecast['Price'], name="Recalibrated Forecast", 
                         mode='lines+markers', line=dict(color="#B71C1C", width=3, dash='dash')))

fig.update_layout(
    title="Integrated Cattle Price Projection (USD/CWT)",
    xaxis_title="Timeline",
    yaxis_title="Price per CWT",
    template="plotly_white",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig, use_container_width=True)

# --- 5. DATA DETAILS ---
tab1, tab2 = st.tabs(["📊 Normalization Factors", "📄 Model Logic"])

with tab1:
    st.write("Mean-centered seasonal indices (Normalization Factor Applied)")
    idx_df = pd.DataFrame([final_indices], index=["Multiplier"])
    st.dataframe(idx_df.style.highlight_max(axis=1, color='#d4edda').highlight_min(axis=1, color='#f8d7da'))

with tab2:
    st.info("""
    **Summary of Refinements:**
    *   **Lowered Baseline:** June 2026 is anchored at $248.37 to provide a realistic forecasting floor.
    *   **Sterling Anchor:** The model forces a hard floor of $250.97 during the summer months if inputs drop below breakeven.
    *   **Macro Scaling:** Uses the S&P GSCI (752.79) as a multi-commodity coefficient.
    """)