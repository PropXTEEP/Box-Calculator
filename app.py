import streamlit as st
import time

# --- SETUP PAGE ---
st.set_page_config(page_title="PropX Box Cut Calculator", layout="centered")

# Custom CSS for bigger buttons and better visibility
st.markdown("""
    <style>
    div.stButton > button:first-child { height: 3em; font-size: 20px; font-weight: bold; }
    [data-testid="stMetricValue"] { font-size: 40px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO & TITLE SECTION ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("https://www.propx.com/wp-content/uploads/2024/07/cropped-PropX-RGB.png", use_container_width=True)
with col_title:
    st.title("Box Cut Calculator")

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

# --- SESSION STATE ---
for key, val in {'running': False, 'elapsed_time': 0.0, 'last_beep_time': 0, 'timer_finished': False}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- INPUTS ---
with st.container(border=True):
    st.subheader("📋 Input Parameters")
    c1, c2 = st.columns(2)
    clean_rate = c1.number_input("Clean Rate (bpm)", min_value=0.0, step=1.0)
    sand_conc = c2.number_input("Sand Conc (ppg)", min_value=0.0, step=0.1)

    c3, c4 = st.columns(2)
    current_weight = c3.number_input("Current Weight (lbs)", min_value=0, step=100)
    target_weight = c4.number_input("Target Weight (lbs)", min_value=0, step=100)

# --- CALCULATIONS ---
lbs_per_min = clean_rate * 42 * sand_conc
weight_to_remove = current_weight - target_weight

if lbs_per_min > 0 and weight_to_remove > 0:
    time_seconds = (weight_to_remove / lbs_per_min) * 60
    
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Sand Rate", f"{lbs_per_min:,.0f} lb/min")
    m2.metric("To Remove", f"{weight_to_remove:,.0f} lbs")
    m3.metric("Goal Time", f"{time_seconds:.1f}s")
    
    # --- TIMER CONTROL ---
    b1, b2, b3 = st.columns(3)
    if b1.button("▶️ START", use_container_width=True):
        st.session_state.running = True
        st.session_state.timer_finished = False
        st.session_state.start_time = time.time() - st.session_state.elapsed_time
        st.rerun()
    if b2.button("⏸️ PAUSE", use_container_width=True):
        st.session_state.running = False
        st.rerun()
    if b3.button("🔄 RESET", use_container_width=True):
        st.session_state.running = False
        st.session_state.elapsed_time = 0.0
        st.session_state.timer_finished = False
        st.rerun()

    timer_placeholder = st.empty()
    progress_placeholder = st.empty()
    alert_placeholder = st.empty()

    if st.session_state.running:
        current_elapsed = time.time() - st.session_state.start_time
        
        if current_elapsed >= time_seconds:
            st.session_state.running = False
            st.session_state.timer_finished = True
            st.session_state.elapsed_time = time_seconds
            play_beep_sequence()
            st.rerun()
        else:
            st.session_state.elapsed_time = current_elapsed
            rem = time_seconds - current_elapsed
            progress = min(current_elapsed / time_seconds, 1.0)
            
            color = "#28a745" if rem > 5 else "#fd7e14"
            if rem <= 5:
                alert_placeholder.warning(f"⚠️ CLOSE THE BOX IN {rem:.1f}s")
                if time.time() - st.session_state.last_beep_time > 1.0:
                    play_beep_sequence()
                    st.session_state.last_beep_time = time.time()

            progress_placeholder.progress(progress)
            timer_placeholder.markdown(
                f"<div style='text-align: center; border: 5px solid {color}; padding: 20px; border-radius: 15px;'>"
                f"<h1 style='color: {color}; font-family: monospace; font-size: 80px;'>{st.session_state.elapsed_time:.1f}s</h1>"
                f"</div>", unsafe_allow_html=True)
            
            time.sleep(0.1)
            st.rerun()
    else:
        # Static displays for Paused/Finished
        if st.session_state.timer_finished:
            alert_placeholder.error("🚨 CUT COMPLETE - CLOSE BOX NOW 🚨")
            timer_placeholder.markdown(f"<div style='text-align: center; border: 5px solid #dc3545; padding: 20px; border-radius: 15px;'><h1 style='color: #dc3545;'>{st.session_state.elapsed_time:.1f}s<br>COMPLETE</h1></div>", unsafe_allow_html=True)
        else:
            timer_placeholder.markdown(f"<div style='text-align: center; border: 5px solid #6c757d; padding: 20px; border-radius: 15px;'><h1 style='color: #6c757d;'>{st.session_state.elapsed_time:.1f}s<br>PAUSED</h1></div>", unsafe_allow_html=True)

elif weight_to_remove < 0:
    st.error("Target weight cannot be greater than current weight.")
else:
    st.info("Waiting for data... Enter Rate, Conc, and Weights to begin.")
