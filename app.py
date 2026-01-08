import streamlit as st
import time
import base64

# Setup the page look
st.set_page_config(page_title="Box Cut Calculator", layout="centered")

st.title("🏗️ PropX Box Cut Calculator!")
st.write("Adjust any value below to update the Run Time instantly.")

# --- AUDIO FUNCTION ---
def play_warning_sound():
    # This is a short, clean 'ping' sound encoded in base64
    # You can replace this with any public URL to an .mp3 file
    audio_html = """
        <audio autoplay>
            <source src="https://raw.githubusercontent.com/propx-audio/assets/main/beep.mp3" type="audio/mp3">
        </audio>
    """
    st.components.v1.html(audio_html, height=0)

# --- STOPWATCH SESSION STATE INITIALIZATION ---
if 'running' not in st.session_state:
    st.session_state.running = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0
if 'alarm_fired' not in st.session_state:
    st.session_state.alarm_fired = False

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
lbs_per_min = clean_rate * 42 * sand_conc
weight_to_remove = current_weight - target_weight

st.divider()

# --- OUTPUT SECTION ---
if lbs_per_min > 0 and weight_to_remove > 0:
    time_seconds = (weight_to_remove / lbs_per_min) * 60
    
    m1, m2 = st.columns(2)
    m1.metric("Sand Rate", f"{lbs_per_min:,.0f} lb/min")
    m2.metric("Amount to be ran", f"{weight_to_remove:,.0f} lbs")
    
    st.success(f"## ⏱️ CLOSE BOX AFTER: {time_seconds:.1f} SECONDS")
    
    # --- STOPWATCH MODULE ---
    st.subheader("Stopwatch Timer")
    
    c1, c2, c3 = st.columns(3)
    if c1.button("Start / Resume"):
        if not st.session_state.running:
            st.session_state.start_time = time.time() - st.session_state.elapsed_time
            st.session_state.running = True
    if c2.button("Stop / Pause"):
        st.session_state.running = False
    if c3.button("Reset"):
        st.session_state.running = False
        st.session_state.elapsed_time = 0
        st.session_state.alarm_fired = False

    timer_placeholder = st.empty()
    alert_placeholder = st.empty()
    
    while st.session_state.running:
        st.session_state.elapsed_time = time.time() - st.session_state.start_time
        remaining_time = time_seconds - st.session_state.elapsed_time
        
        # Determine Color and Alerts
        if remaining_time > 5:
            color = "green"
            alert_placeholder.empty()
            st.session_state.alarm_fired = False # Reset alarm if timer is reset/adjusted
        elif 0 < remaining_time <= 5:
            color = "orange"
            alert_placeholder.warning(f"⚠️ GET READY: {remaining_time:.1f}s REMAINING")
            
            # Fire the sound once
            if not st.session_state.alarm_fired:
                play_warning_sound()
                st.session_state.alarm_fired = True
        else:
            color = "red"
            alert_placeholder.error("🚨 CLOSE BOX NOW! 🚨")
        
        timer_placeholder.markdown(
            f"<h1 style='text-align: center; color: {color}; font-family: monospace;'>"
            f"{st.session_state.elapsed_time:.1f} / {time_seconds:.1f} s</h1>", 
            unsafe_allow_html=True
        )
            
        time.sleep(0.1)
        st.rerun()

    # Static display when not running
    if not st.session_state.running:
        timer_placeholder.markdown(
            f"<h1 style='text-align: center; color: grey; font-family: monospace;'>"
            f"{st.session_state.elapsed_time:.1f} / {time_seconds:.1f} s</h1>", 
            unsafe_allow_html=True
        )

    st.divider()
    progress_val = min(target_weight / current_weight, 1.0) if current_weight > 0 else 0
    st.progress(progress_val, text=f"Target is {progress_val:.1%} of current weight")

elif weight_to_remove <= 0 and current_weight > 0:
    st.error("Target weight must be lower than current weight.")
else:
    st.info("Enter values above to calculate.")
