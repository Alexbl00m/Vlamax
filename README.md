# Vlamax

Single-File Streamlit App for Metabolic Analysis

Developing a single-file Streamlit application with all features integrated involves careful planning. Below, we outline how to implement each requirement (UI design, input handling, charts, zone calculations, PDF export, caching, etc.) in one cohesive app.py script. We also include code snippets and best practices for clarity.

1. Branded UI with Lindblom Coaching Theme

To present a professional, branded interface, we utilize Streamlit’s theming and include the Lindblom Coaching logo and colors:
	•	Theming: Streamlit allows custom theming via a config file or CLI flags ￼. In a single-file app, the easiest way is to create a .streamlit/config.toml alongside the script with a [theme] section. For example:

[theme]
primaryColor="#123456" 
backgroundColor="#FFFFFF" 
secondaryBackgroundColor="#F0F2F6" 
textColor="#000000"
font="sans serif"

(Replace #123456 with Lindblom Coaching’s actual primary color.) This sets the app’s accent color (for buttons, sliders, etc.), background colors, text color, and font ￼. All Streamlit components will automatically use these theme colors for a cohesive look.

	•	Logo and Branding: We display the Lindblom Coaching logo at the top of the app (e.g., in the sidebar or main header). Streamlit’s st.image can show the logo from a local file or URL. For instance:

st.set_page_config(page_title="Lindblom Coaching - Metabolic Analysis", page_icon=":running:")
st.image("Logotype_Light@2x.png", width=200)
st.title("Metabolic Analysis Report")
st.markdown("**Coach:** Alexander Lindblom")  # example branding text

Here, st.set_page_config sets the page title and tab icon. We then show the logo image (ensuring the file is in the same directory) and some branded text. The Lindblom Coaching colors will reflect in UI elements thanks to the custom theme. We can further fine-tune styling with HTML/CSS in st.markdown if needed (e.g., coloring specific text in the brand’s color), but using the built-in theming is simpler and maintainable.

	•	Layout: We keep the layout centered and use Streamlit columns or sidebar for better presentation. For example, important inputs can be placed in a sidebar with st.sidebar.header("Inputs") to separate them from results.

2. User Input Form and Validation

We gather all required physiological inputs through a form so that users can enter data and submit once:
	•	Input Fields: We use st.form to batch inputs and a submit button. This prevents the app from updating on each field change, only running when the user clicks “Submit”. For example:

with st.form("input_form"):
    vo2max = st.number_input("VO₂max (ml/kg/min)", min_value=0.0, format="%.1f")
    lt1_hr = st.number_input("LT1 (Aerobic Threshold HR, bpm)", min_value=0)
    lt2_hr = st.number_input("LT2 (Anaerobic Threshold HR, bpm)", min_value=0)
    max_hr = st.number_input("Max Heart Rate (bpm)", min_value=0)
    sprint_power = st.number_input("Sprint Power 5s (W)", min_value=0)
    # ... other inputs as needed
    notes = st.text_area("Athlete Notes (optional)")
    submitted = st.form_submit_button("Analyze")

This creates a form with fields for VO₂max, LT1 HR, LT2 HR, max HR, sprint power, etc., and a multiline text area for any notes. We use number_input for numerical data with sensible minimums (e.g., no negative values). The submitted flag becomes True when the user presses Analyze.

	•	Validation: After submission, we validate inputs in code. For instance, we ensure no field is left blank or zero (aside from optional notes). We can check each value and use st.error to prompt the user if something is off:

if submitted:
    # Basic validation checks
    if vo2max <= 0 or lt1_hr <= 0 or lt2_hr <= 0 or max_hr <= 0 or sprint_power <= 0:
        st.error("Please enter all required fields with valid (non-zero) values.")
    elif not (lt1_hr < lt2_hr < max_hr):
        st.error("Ensure that LT1 HR < LT2 HR < Max HR for consistency.")
    else:
        st.success("Inputs look good! Generating analysis...")
        # Proceed to calculations and outputs...

This way, the app only proceeds if inputs are plausible. The form mechanism makes all inputs available at once when submitted, simplifying validation logic (no need for complex callback handling) ￼.
Note: Streamlit forms do not natively prevent submission on invalid input, so manual checks like above are essential for required fields ￼. We also included a logical check that LT1 < LT2 < HR_max, which should generally hold for real physiology.

3. Interactive Charts and Visualizations

A core feature is plotting various metabolic curves based on the input data. We will create four interactive charts: Lactate Curve, VO₂ Kinetics/Oxygen Demand, and Energy Expenditure. Using Plotly (via plotly.express or graph_objects) provides interactive capabilities (hover info, zoom, save as image) with minimal effort ￼ ￼. We could also use Altair (st.altair_chart), but we’ll illustrate with Plotly here.

Lactate Curve: This chart plots blood lactate concentration versus exercise intensity. Typically, intensity can be represented by power (W) or pace, and we expect an exponential rise in lactate as intensity increases. We can simulate a lactate curve using the VO₂max and sprint power inputs (which inform aerobic vs anaerobic capacity). For example, we create a range of intensities from easy to max and estimate lactate at each point. Then we plot:

import numpy as np
import plotly.express as px

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

This code generates a lactate curve with dummy logic: lactate ~1 mmol at low effort, then rising around two breakpoints (assumed at 60% and 90% of sprint power as proxies for LT1 and LT2 intensity). Vertical lines mark the LT1 and LT2 points. In practice, if actual lactate measurements or a physiological model were available, you’d use those. The resulting Plotly line chart is interactive in the app – users can hover to see exact values, zoom into regions, etc. ￼.

￼ ￼

Example lactate threshold curve showing how blood lactate (mmol/L) rises with increasing intensity (Watts). Key thresholds LT1 and LT2 are points where lactate accumulation shows a sustained increase ￼.

VO₂ Kinetics & Oxygen Demand: Here we illustrate how oxygen uptake responds over time when exercise intensity suddenly changes (e.g., at exercise onset or transitions). VO₂ kinetics often follow an exponential curve to steady-state ￼, and a concept of oxygen deficit applies – at the start of exercise, VO₂ lags behind the immediate oxygen demand, and the difference is met by anaerobic sources ￼ ￼. We can simulate a simple scenario: an athlete goes from rest to a constant workload (say, at LT2 intensity) at time t=0. VO₂ will rise gradually to meet the demand. We plot both the required O₂ (demand) and actual VO₂ over time:

import plotly.graph_objects as go

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

This produces a Plotly chart with two lines: a dashed horizontal line for the constant oxygen demand, and a rising curve for VO₂ actually consumed. The area between them at the beginning represents the O₂ deficit (made up by anaerobic energy) ￼ ￼. Such a chart helps users see how quickly they attain steady-state and how their aerobic system responds.

Energy Expenditure (Fat vs Carb): We also visualize how the mix of energy sources shifts with intensity. Typically, at lower intensities (around LT1), a higher fraction of energy comes from fat, and as intensity increases towards LT2 and beyond, carbohydrate usage dominates. If we assume we know the maximal fat oxidation (FatMax) occurs near LT1, we can plot calories from fat and carbs per minute across a range of intensities. For example:

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

This uses a stacked area chart (Plotly Express area with stackgroup) to show fat vs carb contribution. At low intensity, the Fat area is large (more teal area), and at high intensity the Carb area (red) dominates, illustrating the “crossover” concept. Users can hover to see exact kcal/min from each source at a given intensity. This chart ties in with the LT1 (FatMax) point – around LT1 the fat contribution peaks ￼ ￼.

All these charts are interactive. We use use_container_width=True so they resize nicely with the app layout ￼. The color palette and font will automatically match the theme (Streamlit can apply its theme to Plotly charts as well, or we can manually set colors to align with Lindblom branding).

4. Heart Rate Zone Calculation

Using the provided thresholds (LT1, LT2, and max HR), we compute personalized heart rate training zones. These zones help translate the lab metrics into actionable training intensity ranges.

Defining Zones: There are multiple ways to define HR zones. A simple approach is a 3-zone model (popular in polarized training) where: Zone 1 is <LT1, Zone 2 is between LT1 and LT2, Zone 3 is >LT2 ￼. However, many coaches use 5 to 7 zones for finer granularity. We’ll demonstrate a 5-zone scheme using LT1, LT2, and HR_max:
	•	Zone 1 (Recovery/Easy): Heart rates below LT1. This is low intensity, primarily aerobic metabolism.
	•	Zone 2 (Endurance): Heart rate from LT1 up to a midpoint between LT1 and LT2. Comfortable steady efforts in this zone.
	•	Zone 3 (Tempo/Moderate): Heart rates around LT2 (Anaerobic Threshold). This zone borders the maximal steady-state effort (roughly lactate steady state).
	•	Zone 4 (Interval/Hard): Heart rates between LT2 and ~95% of HR_max. High intensity, approaching VO₂max.
	•	Zone 5 (Maximal): Heart rates from 95% HR_max to HR_max (near all-out effort).

We compute the boundaries in beats per minute (bpm). For example:

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

This creates a dictionary of zone names to HR ranges and then displays them. We used a simple heuristic: Zone2/3 split at midpoint between LT1 and LT2, and Zone4/5 split at 95% HRmax. In practice, one could refine these percentages or add more zones (Zone 6/7 for anaerobic capacity and sprint, if needed ￼). The idea is to tailor the zones around the athlete’s physiological landmarks rather than generic formulas ￼ ￼.

For example, if LT1 = 140 bpm, LT2 = 170 bpm, HR_max = 190 bpm:
	•	Zone1: <140 bpm
	•	Zone2: 140–155 bpm
	•	Zone3: 155–170 bpm
	•	Zone4: 170–180 bpm
	•	Zone5: 180–190 bpm

This output is clearly structured for the user. We can present it as text or as a table. A small DataFrame could also be used and shown with st.table for a cleaner look.

5. PDF Report Generation and Download

The application can generate a professional PDF report summarizing the results, so coaches or athletes can save their data. We use the FPDF library (a lightweight PDF generator) to compose the report, then offer it for download.

Generating the PDF: We create an FPDF object, add pages, and write content (text, images, lines, etc.). This will include:
	•	The header with Lindblom Coaching logo and contact info (we can subclass FPDF to create a custom header/footer if needed).
	•	Test summary: listing input data (VO₂max, LT1, LT2, etc.).
	•	Heart Rate Zones table.
	•	Charts: We can save the Plotly charts as images and then insert into PDF, or re-generate similar static charts via matplotlib for embedding. (Plotly can export to PNG via fig.write_image if kaleido is installed.)
	•	Athlete Notes: include the notes the user entered.

Because we want a single-file solution, ensure any font files or images (like logo) used by FPDF are accessible. We can use the same Logotype_Light@2x.png for the PDF header.

For example, using FPDF:

from fpdf import FPDF

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

This is a simplified example. We would likely format it more nicely (e.g., use cells to create columns, lines, or shading for tables). The FPDF documentation can be referenced for advanced layout, or reuse patterns from the existing Lindblom Coaching report code (the provided snippet in the question shows custom classes adding sections, fonts like ‘Exo’, etc.). The result is a PDF in memory.

Downloading the PDF: To let the user download, we use st.download_button. We must output the PDF as bytes. Using FPDF, we call pdf.output(dest='S').encode('latin-1') to get the PDF content (FPDF outputs as Latin-1 encoded string by default) ￼ ￼. For example:

pdf_bytes = pdf.output(dest='S').encode('latin-1')
st.download_button("Download PDF Report", data=pdf_bytes, file_name="Metabolic_Report.pdf", mime="application/pdf")

When the user clicks this button, Streamlit will send the PDF file to their browser to download. The mime type ensures it’s recognized as a PDF. We use the encoding because in Python 3, FPDF’s output needs Latin-1 bytes to produce a valid PDF ￼ ￼.

By packaging the report generation in a function (and possibly using @st.cache_data if it’s heavy), we ensure the app remains responsive. The user can adjust inputs and generate a new PDF as needed. All of this happens within the single script, and the PDF never touches disk – it’s generated and downloaded from memory, which is convenient and secure ￼ ￼.

(If needed, we can also display the PDF in-app using st.download_button or embed via st.components.v1.html with a base64 PDF, but a direct download is simplest.)

6. Performance Optimization with Caching

Streamlit reruns the script on each interaction, so using caching can significantly improve performance for expensive computations ￼ ￼. In this app, potential heavy operations include: complex metabolic calculations, loading of large libraries or data, or generating high-resolution charts/PDFs. We leverage st.cache_data for these:
	•	Decorate functions that compute data (not just UI). For example, if we had a function simulate_lactate_curve(vo2max, sprint_power) that does a lot of math or perhaps even calls an external API or large dataset, we can do:

@st.cache_data
def simulate_lactate_curve(vo2max, sprint_power):
    # expensive calculations...
    return lactate_values

On subsequent runs with the same inputs, Streamlit will use the cached result instead of recomputing, speeding things up ￼ ￼. Because we included input parameters (vo2max, sprint_power), the cache is invalidated if the user inputs change, ensuring freshness.

	•	We can also cache the PDF generation if it involves heavy plotting or data assembly. For instance, if generating images for the PDF takes time, cache the final PDF bytes for given inputs.
	•	Use st.cache_resource for caching resources like loading a machine learning model or a large dataset that doesn’t change with each run ￼. In our case, maybe loading custom fonts for FPDF or any one-time setups can be cached.

By optimizing with caching, the app avoids redundant recalculations. For example, if a user toggles a minor setting that doesn’t affect the lactate curve data, the cached curve can be reused ￼. We should be careful to cache only deterministic functions and be mindful of memory (cache stores data in memory). Fortunately, our use-case deals with relatively small data (a few numbers and small images), so caching is mainly about speed.

7. Modular Single-File Implementation

Even though everything resides in one app.py file, we keep the code modular and readable by splitting logic into sections and functions:
	•	Imports and Config at the top (Streamlit, Plotly, FPDF, NumPy, etc.), and perhaps a section to set the theme (like reading config or applying CSS if needed).
	•	Define helper functions for repetitive tasks. For example, def calculate_zones(lt1, lt2, max_hr): ... returns the zones dict, or def create_pdf(...): ... returns PDF bytes. Mark these with @st.cache_data if appropriate. This makes the main app flow easier to follow.
	•	Main App Flow: Use comments or headers in the code to separate steps: input form, validations, calculations, charts, outputs. Streamlit allows writing markdown text as documentation in the app, but here we refer to structuring the code itself. For example:

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

This kind of structure (using comments or even st.markdown("---") as a divider in the UI) ensures maintainability. If the code grows, you can still keep it in one file but logically separated.

	•	No external dependencies beyond this file: ensure any images (logo) or custom fonts are shipped with the file or encoded. For example, one could base64-encode the logo and use pdf.image(stream=BytesIO(base64.b64decode(...))) to avoid separate files. But since the prompt allows a single script, having the image in the same folder is acceptable.

Finally, the app can be run with streamlit run app.py. All features will load: the UI shows the branded header and form, the user submits data, then interactive charts render and zones text appears, and a PDF download link is provided. Thanks to caching and efficient coding, the experience will be smooth and fast.

By following this approach, we meet all requirements: a nicely themed UI, robust input handling, dynamic visualizations, personalized training zones, PDF report generation, and performance optimizations – all implemented in a single Python script for Streamlit.