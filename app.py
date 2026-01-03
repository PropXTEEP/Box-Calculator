import streamlit as st

# Setup the page look
st.set_page_config(page_title="Box Cut Calculator", layout="centered")

st.title("🏗️ PropX Box Cut Calculator")
st.write("Adjust any value below to update the Run Time instantly.")

# --- INPUT SECTION ---
st.subheader("1. Frac's Rate & Conc")
col_top1, col_top2 = st.columns(2)

with col_top1:
    clean_rate = st.number_input("Clean Rate (bbls/min)", min_value=0.0, step=0.1, value=80.0)

with col_top2:
    sand_conc = st.number_input("Sand Concentration (ppg)", min_value=0.0, step=0.1, value=2.0)

st.subheader("2. Box Weights")
col_bot1, col_bot2 = st.columns(2)

with col_bot1:
    current_weight = st.number_input("Cut Box's Full Weight (lbs)", min_value=0, step=100, value=22500)

with col_bot2:
    target_weight = st.number_input("Target End Weight (lbs)", min_value=0, step=100, value=11000)

# --- CALCULATION LOGIC ---
# lbs/min = Clean Rate * 42 (gal/bbl) * Concentration
lbs_per_min = clean_rate * 42 * sand_conc
weight_to_remove = current_weight - target_weight

st.divider()

# --- OUTPUT SECTION ---
if lbs_per_min > 0 and weight_to_remove > 0:
    time_seconds = (weight_to_remove / lbs_per_min) * 60
    
    # Large displays for easy reading on the fly
    m1, m2 = st.columns(2)
    m1.metric("Sand Rate", f"{lbs_per_min:,.0f} lb/min")
    m2.metric("Amount to be ran", f"{weight_to_remove:,.0f} lbs")
    
    # The Big Result
    st.success(f"## ⏱️ CLOSE BOX AFTER: {time_seconds:.1f} SECONDS")
    
    # Visual Progress
    progress_val = min(target_weight / current_weight, 1.0) if current_weight > 0 else 0
    st.progress(progress_val, text=f"Target is {progress_val:.1%} of current weight")

elif weight_to_remove <= 0 and current_weight > 0:
    st.error("Target weight must be lower than current weight.")
else:
    st.info("Enter values above to calculate.")
