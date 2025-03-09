import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF

# Set page configuration (must be before any Streamlit commands)
st.set_page_config(page_title=\"Lindblom Coaching - Metabolic Analysis\", page_icon=\":running:\")
st.image("Logotype_Light@2x.png", width=200)
st.title("Metabolic Analysis Report")
st.markdown("**Coach:** Alexander Lindblom")  # example branding text

with st.form("input_form"):
    vo2max = st.number_input("VO₂max (ml/kg/min)", min_value=0.0, format="%.1f")
    lt1_hr = st.number_input("LT1 (Aerobic Threshold HR, bpm)", min_value=0)
    lt2_hr = st.number_input("LT2 (Anaerobic Threshold HR, bpm)", min_value=0)
    max_hr = st.number_input("Max Heart Rate (bpm)", min_value=0)
    sprint_power = st.number_input("Sprint Power 5s (W)", min_value=0)
    # ... other inputs as needed
    notes = st.text_area("Athlete Notes (optional)")
    submitted = st.form_submit_button("Analyze")
    
    
if submitted:
    # Basic validation checks
    if vo2max <= 0 or lt1_hr <= 0 or lt2_hr <= 0 or max_hr <= 0 or sprint_power <= 0:
        st.error("Please enter all required fields with valid (non-zero) values.")
    elif not (lt1_hr < lt2_hr < max_hr):
        st.error("Ensure that LT1 HR < LT2 HR < Max HR for consistency.")
    else:
        st.success("Inputs look good! Generating analysis...")
        # Proceed to calculations and outputs..

# Simulate lactate curve data (for demonstration purposes)
intensities = np.linspace(0.4, 1.1, 15) * sprint_power  # 40% to 110% of sprint power
# Simple model: lactate starts ~1 mmol, rises faster after LT1 and LT2
lactate = []
for p in intensities:
    if p < 0.6 * sprint_power:
        lactate.append(1 + 0.5 * (p/(0.6*sprint_power)))  # slow rise
    elif p < 0.9 * sprint_power:
        lactate.append(1.5 + 2 * ((p - 0.6*sprint_power)/(0.3*sprint_power)))  # moderate rise
    else:
        lactate.append(3.5 + 5 * ((p - 0.9*sprint_power)/(0.2*sprint_power)))  # sharp rise near max
lactate = np.array(lactate)

fig_lactate = px.line(x=intensities, y=lactate, markers=True,
                      labels={"x": "Intensity (W)", "y": "Blood Lactate (mmol/L)"},
                      title="Lactate Profile Curve")
# Mark LT1 and LT2 points on the curve if known (using HR values might require converting to intensity; here assume proportional to sprint_power)
fig_lactate.add_vline(x=0.6 * sprint_power, line_dash="dash", line_color="green", annotation_text="LT1")
fig_lactate.add_vline(x=0.9 * sprint_power, line_dash="dash", line_color="red", annotation_text="LT2")
st.plotly_chart(fig_lactate, use_container_width=True)


time = np.arange(0, 300, 5)  # 5-minute exercise, data points every 5s
tau = 40  # time constant for VO2 kinetics (example: 40s to reach ~63% of final VO2)
vo2_steady = vo2max * 0.85  # assume steady-state VO2 at this intensity is 85% of VO2max
vo2_actual = vo2_steady * (1 - np.exp(-time/tau))  # VO2 rises exponentially to steady state
o2_demand = np.full_like(time, vo2_steady)  # constant O2 requirement once exercise starts

fig_vo2 = go.Figure()
fig_vo2.add_trace(go.Scatter(x=time, y=o2_demand, mode='lines', name='O₂ Demand', line=dict(dash='dash')))
fig_vo2.add_trace(go.Scatter(x=time, y=vo2_actual, mode='lines', name='VO₂ uptake', line=dict(color='firebrick')))
fig_vo2.update_layout(title="VO₂ Kinetics at Exercise Onset", xaxis_title="Time (s)", yaxis_title="O₂ (ml/kg/min)")
st.plotly_chart(fig_vo2, use_container_width=True)

intensity_pct = np.linspace(50, 100, 11)  # 50% to 100% intensity
# Assumed proportions (for demo): at 50% intensity, 80% energy from fat; at 100%, 0% from fat.
fat_pct = np.clip(80 - 8*(intensity_pct-50)/5, 0, 80)  # linear decline from 80% to 0%
carb_pct = 100 - fat_pct
total_cal = 10  # assume 10 kcal/min at 50% and scale up
calories = total_cal * (intensity_pct/50)  # simplistic scaling of total cal burn rate
fat_cal = calories * fat_pct/100
carb_cal = calories * carb_pct/100

fig_energy = px.area(x=intensity_pct, y=[fat_cal, carb_cal], labels={"x": "% Intensity", "value": "Kcal/min"},
                     title="Energy Expenditure by Fuel Source", color_discrete_sequence=["#72B7B2","#EF553B"])
fig_energy.update_traces(stackgroup="one", names=["Fat", "Carbohydrate"])
st.plotly_chart(fig_energy, use_container_width=True)

# Ensure LT1, LT2, HR_max are valid (done in validation)
LT1 = lt1_hr
LT2 = lt2_hr
HRmax = max_hr
# Define zones:
zones = {
    "Zone 1 (Easy/Recovery)": (0, LT1),
    "Zone 2 (Endurance)": (LT1, (LT1+LT2)/2),
    "Zone 3 (Threshold)": ((LT1+LT2)/2, LT2),
    "Zone 4 (Interval)": (LT2, 0.95*HRmax),
    "Zone 5 (Max Effort)": (0.95*HRmax, HRmax)
}
# Display zones
st.subheader("Personalized Heart Rate Zones")
for zone, (low, high) in zones.items():
    st.write(f"**{zone}:** {low:.0f}–{high:.0f} bpm")

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", 'B', 16)
# Header with logo
pdf.image("Logotype_Light@2x.png", x=10, y=8, w=30)  # adjust x, y, width as needed
pdf.cell(0, 10, "Lindblom Coaching – Metabolic Test Report", ln=True, align='C')
pdf.ln(10)
# Summary text
pdf.set_font("Arial", '', 12)
pdf.cell(0, 10, f"VO₂max: {vo2max:.1f} ml/kg/min", ln=True)
pdf.cell(0, 10, f"LT1 HR: {LT1:.0f} bpm    LT2 HR: {LT2:.0f} bpm    Max HR: {HRmax:.0f} bpm", ln=True)
pdf.cell(0, 10, f"Sprint Power (5s): {sprint_power:.0f} W", ln=True)
pdf.ln(5)
# Zones table
pdf.set_font("Arial", 'B', 12)
pdf.cell(0, 10, "Heart Rate Zones:", ln=True)
pdf.set_font("Arial", '', 12)
for zone, (low, high) in zones.items():
    pdf.cell(0, 8, f"{zone}: {low:.0f}-{high:.0f} bpm", ln=True)
pdf.ln(5)
# Notes
if notes:
    pdf.multi_cell(0, 8, f"Athlete Notes: {notes}")
    
pdf_bytes = pdf.output(dest='S').encode('latin-1')
st.download_button("Download PDF Report", data=pdf_bytes, file_name="Metabolic_Report.pdf", mime="application/pdf")

@st.cache_data
def simulate_lactate_curve(vo2max, sprint_power):
    # expensive calculations...
    return lactate_values
    
    
# --- Input Section ---
st.header("Input Data")
# (form code here)

# --- Validation and Calculations ---
if submitted:
    # validate...
    # calculate zones, curves...

    # --- Output Results ---
    st.header("Results")
    # display charts and zones

    # --- PDF Generation ---
    pdf_bytes = create_pdf(...)  # our helper
    st.download_button("Download PDF", pdf_bytes, file_name="report.pdf")
