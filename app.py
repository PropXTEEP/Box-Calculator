import streamlit as st
import time

st.set_page_config(page_title="Box Cut Calculator", layout="centered")

st.title("🏗️ PropX Box Cut Calculator")

# --- AUDIO COMPONENT ---
def play_beep_sequence():
    js_code = """
    <script>
    (function() {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') { audioCtx.resume(); }
        const now = audioCtx.currentTime;
        [0, 0.15, 0.3].forEach(delay => {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'square'; 
            osc.frequency.setValueAtTime(880, now + delay);
            gain.gain.setValueAtTime(0.5, now + delay);
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

# --- SESSION STATE INITIALIZATION ---
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
    clean_rate = st.number_input("Clean Rate (bpm)", min_value=0.0, value=80.0)
with col_top2:
    sand_conc = st.number_input("Sand Conc (ppg)", min_value=0.0, value=2.0)

st.subheader("2. Box Weights")
col_bot1, col_bot2 = st.columns(2)
with col_bot1:
    current_weight = st.number_input("Full Weight (lbs)", min_value=0, value=22500)
with col_bot2:
    target_weight = st.number_input("Target Weight (lbs)", min_value=0, value=11000)

# --- CALCULATIONS ---
# lb/min = bpm * 42 gal/bbl * ppg
lbs_per_min = clean_rate * 42 * sand_conc
weight_to_remove = current_weight - target_weight

if lbs_per_min > 0 and weight_to_remove > 0:
    time_seconds = (weight_to_remove / lbs_per_min) * 60
    
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Sand Rate", f"{lbs_per_min:,.0f} lb/m")
    m2.metric("Removal", f"{weight_to_remove:,.0f} lbs")
    m3.metric("Target Time", f"{time_seconds:.1f}s")
    
    # --- STOPWATCH UI ---
    st.subheader("Stopwatch Timer")
    c1, c2, c3 = st.columns(3)
    
    if c1.button("▶️ Start / Resume", use_container_width=True):
        if not st.session_state.running:
            st.session_state.running = True
            st.session_state.start_time = time.time() - st.session_state.elapsed_time
            st.rerun()
        
    if c2.button("⏸️ Pause", use_container_width=True):
        st.session_state.running = False
        st.rerun()
        
    if c3.button("🔄 Reset", use_container_width=True):
        st.session_state.running = False
        st.session_state.elapsed_time = 0
        st.session_state.last_beep_time = 0
        st.rerun()

    timer_placeholder = st.empty()
    alert_placeholder = st.empty()
    
    if st.session_state.running:
        st.session_state.elapsed_time = time.time() - st.session_state.start_time
        rem = time_seconds - st.session_state.elapsed_time
        
        # UI Logic based on time remaining
        if rem > 5:
            color = "#28a745" # Green
        elif 0 < rem <= 5:
            color = "#fd7e14" # Orange
            alert_placeholder.warning(f"⚠️ START CLOSING NOW!! {rem:.1f}s")
            if time.time() - st.session_state.last_beep_time > 1.0:
                play_beep_sequence()
                st.session_state.last_beep_time = time.time()
        else:
            color = "#dc3545" # Red
            alert_placeholder.error("🚨 BOX SHOULD BE CLOSED!! 🚨")
            if time.time() - st.session_state.last_beep_time > 0.5:
                play_beep_sequence()
                st.session_state.last_beep_time = time.time()

        timer_placeholder.markdown(
            f"<div style='text-align: center; border: 5px solid {color}; padding: 10px; border-radius: 15px;'>"
            f"<h1 style='color: {color}; font-family: monospace; font-size: 60px; margin-bottom: 0;'>"
            f"{st.session_state.elapsed_time:.1f}s</h1>"
            f"<p style='color: grey;'>Target: {time_seconds:.1f}s</p></div>", 
            unsafe_allow_html=True
        )
        
        time.sleep(0.1)
        st.rerun()
    else:
        timer_placeholder.markdown(
            f"<div style='text-align: center; border: 5px solid #6c757d; padding: 10px; border-radius: 15px;'>"
            f"<h1 style='color: #6c757d; font-family: monospace; font-size: 60px; margin-bottom: 0;'>"
            f"{st.session_state.elapsed_time:.1f}s</h1>"
            f"<p style='color: grey;'>Paused (Target: {time_seconds:.1f}s)</p></div>", 
            unsafe_allow_html=True
        )
else:
    st.info("Enter values above to calculate run time.")
