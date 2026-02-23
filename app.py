import streamlit as st
import time

# --- SETUP PAGE ---
st.set_page_config(page_title="Box Cut Calculator", layout="centered")

# --- LOGO & TITLE SECTION (UPDATED) ---
# Create two columns: small one for logo, big one for title
col_logo, col_title = st.columns([1, 5])

with col_logo:
# Replace this URL with your local file path, e.g., "propx_logo.png"
st.image("https://www.propx.com/wp-content/uploads/2024/07/cropped-PropX-RGB.png", use_container_width=True)

with col_title:
    st.title("PropX Box Cut Calculator")
    st.title("Box Cut Calculator")

# --- AUDIO COMPONENT ---
def play_beep_sequence():
js_code = """
   <script>
   (function() {
       const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
       if (audioCtx.state === 'suspended') { audioCtx.resume(); }
       const now = audioCtx.currentTime;
       
       // Play 3 beeps
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
if 'running' not in st.session_state:
st.session_state.running = False
if 'elapsed_time' not in st.session_state:
st.session_state.elapsed_time = 0.0
if 'last_beep_time' not in st.session_state:
st.session_state.last_beep_time = 0
if 'timer_finished' not in st.session_state:
st.session_state.timer_finished = False

# --- INPUTS ---
st.subheader("1. Frac's Rate & Conc")
c1, c2 = st.columns(2)
with c1:
clean_rate = st.number_input("Clean Rate (bbls/min)", min_value=0.0, value=0.0, step=1.0)
with c2:
sand_conc = st.number_input("Sand Conc (ppg)", min_value=0.0, value=0.0, step=0.1)

st.subheader("2. Box Weights")
c3, c4 = st.columns(2)
with c3:
current_weight = st.number_input("Full Weight (lbs)", min_value=0, value=0, step=100)
with c4:
target_weight = st.number_input("Target End Weight (lbs)", min_value=0, value=0, step=100)

# --- CALCULATIONS ---
lbs_per_min = clean_rate * 42 * sand_conc
weight_to_remove = current_weight - target_weight

if lbs_per_min > 0 and weight_to_remove > 0:
time_seconds = (weight_to_remove / lbs_per_min) * 60

st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("Sand Rate", f"{lbs_per_min:,.0f} lb/min")
m2.metric("Removal Amount", f"{weight_to_remove:,.0f} lbs")
m3.metric("Target Time", f"{time_seconds:.1f}s")

# --- TIMER CONTROL ---
st.subheader("Stopwatch Timer")
b1, b2, b3 = st.columns(3)

# Start Button
if b1.button("▶️ Start / Resume", use_container_width=True):
st.session_state.running = True
st.session_state.timer_finished = False
# Calculate new start time based on what was already elapsed
st.session_state.start_time = time.time() - st.session_state.elapsed_time
st.rerun()

# Pause Button
if b2.button("⏸️ Pause", use_container_width=True):
st.session_state.running = False
st.rerun()

# Reset Button
if b3.button("🔄 Reset", use_container_width=True):
st.session_state.running = False
st.session_state.elapsed_time = 0.0
st.session_state.timer_finished = False
st.rerun()

timer_placeholder = st.empty()
alert_placeholder = st.empty()

# --- TIMER LOGIC ---
if st.session_state.running:
# Calculate current elapsed time
current_elapsed = time.time() - st.session_state.start_time

# CHECK: Have we hit the target?
if current_elapsed >= time_seconds:
# STOP EVERYTHING
st.session_state.running = False
st.session_state.timer_finished = True
st.session_state.elapsed_time = time_seconds # Clamp to exact time
play_beep_sequence() # One final beep
st.rerun() # Force UI update to show "Done" state
else:
# Normal counting
st.session_state.elapsed_time = current_elapsed
rem = time_seconds - current_elapsed

# Colors and Alerts while running
if rem > 5:
color = "#28a745" # Green
else:
color = "#fd7e14" # Orange
alert_placeholder.warning(f"⚠️ START CLOSING THE BOX!! {rem:.1f}s")
# Beep every 1s if close
if time.time() - st.session_state.last_beep_time > 1.0:
play_beep_sequence()
st.session_state.last_beep_time = time.time()

# Display Running Timer
timer_placeholder.markdown(
f"<div style='text-align: center; border: 5px solid {color}; padding: 10px; border-radius: 15px;'>"
f"<h1 style='color: {color}; font-family: monospace; font-size: 60px; margin-bottom: 0;'>"
f"{st.session_state.elapsed_time:.1f}s</h1>"
f"<p style='color: grey;'>Target: {time_seconds:.1f}s</p></div>", 
unsafe_allow_html=True
)

time.sleep(0.1)
st.rerun()

# --- STOPPED STATE UI ---
else:
# If we finished naturally (hit the time limit)
if st.session_state.timer_finished:
color = "#dc3545" # Red
msg = "CUT COMPLETE"
border_style = f"5px solid {color}"
alert_placeholder.error("🚨 BOX SHOULD BE CLOSED - KEEP BELT RUNNING 🚨")
else:
# If we are just paused manually
color = "#6c757d" # Grey
msg = "PAUSED"
border_style = "5px solid #6c757d"

timer_placeholder.markdown(
f"<div style='text-align: center; border: {border_style}; padding: 10px; border-radius: 15px;'>"
f"<h1 style='color: {color}; font-family: monospace; font-size: 60px; margin-bottom: 0;'>"
f"{st.session_state.elapsed_time:.1f}s</h1>"
f"<p style='color: {color}; font-weight: bold;'>{msg}</p></div>", 
unsafe_allow_html=True
)

else:
st.info("Please enter valid rates and weights to calculate.")
