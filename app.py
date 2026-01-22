import streamlit as st
import time

# Setup the page look
st.set_page_config(page_title="Box Cut Calculator", layout="centered")

st.title("🏗️ PropX Box Cut Calculator")
st.write("Adjust values to update Run Time instantly.")

# --- IMPROVED AUDIO JAVASCRIPT ---
def play_beep_sequence():
    js_code = """
    <script>
    (function() {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        // Browsers require resuming the context after a user gesture
        if (audioCtx.state === 'suspended') { audioCtx.resume(); }
        
        const now = audioCtx.currentTime;
        const freq = 880; 
        const vol = 0.5;  
        
        [0, 0.15, 0.3].forEach(delay => {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'square'; 
            osc.frequency.setValueAtTime(freq, now + delay);
            gain.gain.setValueAtTime(vol, now + delay);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + delay + 0.1);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(now + delay);
            osc.stop(now + delay + 0.1);
        });
    })();
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- SESSION STATE ---
if 'running' not in st.session_state:
    st.session_state.running = False
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0.0
if 'last_beep_time' not in st.session_state:
    st.session_state.last_beep_time = 0

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

# --- CALCULATIONS ---
lbs_per_min = clean_rate * 42 * sand_conc
weight_to_remove = current_weight - target_weight

st.divider()

if lbs_per_min > 0 and weight_to_remove > 0:
    time_seconds = (weight_to_remove / lbs_per_min) * 60
    
    m1, m2 = st.columns(2)
    m1.metric("Sand Rate", f"{lbs_per_min:,.0f} lb/min")
    m2.metric("Amount to remove", f"{weight_to_remove:,.0f} lbs")
    
    st.success(f"### ⏱️ TARGET RUN TIME: {time_seconds:.1f} SECONDS")
    
    # --- STOPWATCH UI ---
    st.subheader("Stopwatch Timer")
    c1, c2, c3 = st.columns(3)
    
    if c1.button("▶️ Start / Resume", use_container_width=True):
        st.session_state.running = True
        st.session_state.start_time = time.time() - st.session_state.elapsed_time
        
    if c2.button("⏸️ Stop / Pause", use_container_width=True):
        st.session_state.running = False
        
    if c3.button("🔄 Reset", use_container_width=True):
        st.session_state.running = False
        st.session_state.elapsed_time = 0
        st.session_state.last_beep_time = 0
        st.rerun()

    timer_placeholder = st.empty()
    alert_placeholder = st.empty()
    
    # --- LIVE LOOP ---
    if st.session_state.running:
        st.session_state.elapsed_time = time.time() - st.session_state.start_time
        rem = time_seconds - st.session_state.elapsed_time
        
        # Color & Alert Logic
        if rem > 5:
            color = "#28a745" # Green
        elif 0 < rem <= 5:
            color = "#fd7e14" # Orange
            alert_placeholder.warning(f"⚠️ START CLOSING THE BOX {rem:.1f}s")
            if time.time() - st.session_state.last_beep_time > 1.0:
                play_beep_sequence()
                st.session_state.last_beep_time = time.time()
        else:
            color = "#dc3545" # Red
            alert_placeholder.error("🚨 BOX SHOULD BE CLOSED! 🚨")
            if time.time() - st.session_state.last_beep_time > 0.5:
                play_beep_sequence()
                st.session_state.last_beep_time = time.time()

        timer_placeholder.markdown(
            f"<div style='text-align: center; border: 2px solid {color}; padding: 20px; border-radius: 10px;'>"
            f"<p style='margin:0; color: grey;'>Elapsed / Target</p>"
            f"<h1 style='color: {color}; font-family: monospace; font-size: 50px;'>"
            f"{st.session_state.elapsed_time:.1f}s / {time_seconds:.1f}s</h1></div>", 
            unsafe_allow_html=True
        )
        
        time.sleep(0.1)
        st.rerun()
    else:
        # Static display
        timer_placeholder.markdown(
            f"<div style='text-align: center; border: 2px solid grey; padding: 20px; border-radius: 10px;'>"
            f"<h1 style='color: grey; font-family: monospace; font-size: 50px;'>"
            f"{st.session_state.elapsed_time:.1f}s / {time_seconds:.1f}s</h1></div>", 
            unsafe_allow_html=True
        )

    st.divider()
    progress_val = min(target_weight / current_weight, 1.0) if current_weight > 0 else 0
    st.progress(progress_val, text=f"Box will be {progress_val:.1%} full at target")

else:
    st.info("Please enter valid positive values for rates and weights.")
