import streamlit as st
import time
import smtplib
from email.message import EmailMessage

# --- CONFIGURATION (Use Streamlit Secrets in Production) ---
# For Gmail: You must use an "App Password," not your regular login.
EMAIL_SENDER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password-here"

# --- SMS GATEWAY MAP ---
CARRIERS = {
    "AT&T": "@txt.att.net",
    "Verizon": "@vtext.com",
    "T-Mobile": "@tmomail.net",
    "Sprint": "@messaging.sprintpcs.com",
    "Cricket": "@mms.cricketwireless.net",
    "Boost": "@myboostmobile.com"
}

def send_free_sms(number, carrier_domain, message):
    recipient = f"{number}{carrier_domain}"
    msg = EmailMessage()
    msg.set_content(message)
    msg["To"] = recipient
    msg["From"] = EMAIL_SENDER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        st.error(f"Text failed: {e}")

# --- SETUP PAGE ---
st.set_page_config(page_title="PropX Box Cut", layout="centered")
st.title("🏗️ PropX Box Cut Calculator")

# --- SESSION STATE ---
if 'running' not in st.session_state: st.session_state.running = False
if 'elapsed_time' not in st.session_state: st.session_state.elapsed_time = 0.0
if 'sms_sent' not in st.session_state: st.session_state.sms_sent = False

# --- SMS SETTINGS ---
with st.sidebar:
    st.header("📱 Alert Settings")
    phone = st.text_input("10-Digit Phone #", placeholder="1234567890")
    carrier = st.selectbox("Carrier", options=list(CARRIERS.keys()))
    st.caption("A text will be sent 10s before the target time.")

# --- INPUTS & CALCULATIONS ---
# (Keeping your original input logic)
clean_rate = st.number_input("Clean Rate (bbls/min)", value=80.0)
sand_conc = st.number_input("Sand Concentration (ppg)", value=2.0)
current_weight = st.number_input("Full Weight (lbs)", value=22500)
target_weight = st.number_input("Target Weight (lbs)", value=11000)

lbs_per_min = clean_rate * 42 * sand_conc
weight_to_remove = current_weight - target_weight

if lbs_per_min > 0 and weight_to_remove > 0:
    time_seconds = (weight_to_remove / lbs_per_min) * 60
    st.success(f"### ⏱️ TARGET RUN TIME: {time_seconds:.1f} SECONDS")

    # --- STOPWATCH CONTROLS ---
    c1, c2, c3 = st.columns(3)
    if c1.button("▶️ Start"):
        st.session_state.running = True
        st.session_state.start_time = time.time() - st.session_state.elapsed_time
    if c2.button("⏸️ Stop"):
        st.session_state.running = False
    if c3.button("🔄 Reset"):
        st.session_state.running = False
        st.session_state.elapsed_time = 0
        st.session_state.sms_sent = False # IMPORTANT: Reset SMS trigger
        st.rerun()

    # --- LIVE LOOP ---
    timer_placeholder = st.empty()
    if st.session_state.running:
        st.session_state.elapsed_time = time.time() - st.session_state.start_time
        rem = time_seconds - st.session_state.elapsed_time

        # 10 SECOND SMS TRIGGER
        if 9.8 <= rem <= 10.2 and not st.session_state.sms_sent:
            if phone:
                msg_body = f"PropX ALERT: 10s left! Close box at {time_seconds:.1f}s"
                send_free_sms(phone, CARRIERS[carrier], msg_body)
                st.session_state.sms_sent = True

        timer_placeholder.metric("Elapsed Time", f"{st.session_state.elapsed_time:.1f}s")
        time.sleep(0.1)
        st.rerun()
