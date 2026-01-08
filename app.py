import streamlit as st
import time

# Setup the page look
st.set_page_config(page_title="Box Cut Calculator", layout="centered")

st.title("🏗️ PropX Box Cut Calculator!")
st.write("Adjust any value below to update the Run Time instantly.")

# --- IMPROVED AUDIO JAVASCRIPT ---
def play_beep_sequence():
    # Increased gain to 0.5 for more volume
    js_code = """
    <script>
    (function() {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const now = audioCtx.currentTime;
        const freq = 880; // Sharp A5 note
        const vol = 0.5;  // Increased Volume
        
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

# --- STOPWATCH SESSION STATE INITIALIZATION ---
if 'running' not in st.session_state:
    st.session_state.running = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0
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
        st.session_state.last_beep_time = 0

    timer_placeholder = st.empty()
    alert_placeholder = st.empty()
    
    while st.session_state.running:
        st.session_state.elapsed_time = time.time() - st.session_state.start_time
        remaining_time = time_seconds - st.session_state.elapsed_time
        
        # --- SOUND LOGIC ---
        # If in the warning zone (5s left), beep every 1.0 seconds
        if 0 < remaining_time <= 5:
            if time.time() - st.session_state.last_beep_time > 1.0:
                play_beep_sequence()
                st.session_state.last_beep_time = time.time()
        
        # If time is UP, beep faster (every 0.5 seconds) for high urgency
        elif remaining_time <= 0:
            if time.time() - st.session_state.last_beep_time > 0.5:
                play_beep_sequence()
                st.session_state.last_beep_time = time.time()

        # Visuals
        if remaining_time > 5:
            color = "green"
            alert_placeholder.empty()
        elif 0 < remaining_time <= 5:
            color = "orange"
            alert_placeholder.warning(f"⚠️ GET READY: {remaining_time:.1f}s REMAINING")
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

else:
    st.info("Enter values above to calculate.")
