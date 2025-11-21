from fpdf import FPDF

# Map each language to its Unicode-compatible font
font_map = {
    "English": ("Arial", None)
}

# Translations for each language
translations = {
    "English": {
        "title": "Heart Disease Risk Report",
        "name": "Patient Name",
        "age": "Age",
        "bp": "Blood Pressure",
        "chol": "Cholesterol",
        "max_hr": "Max Heart Rate",
        "ecg": "ECG Result",
        "risk": "Predicted Risk",
        "disease": "Disease Type"
    }
}

def generate_pdf(name, age, bp, chol, max_hr, ecg, result, language="English"):
    t = translations.get(language, translations["English"])
    font_name, font_path = font_map.get(language, ("Arial", None))

    pdf = FPDF()
    pdf.add_page()

    # Register Unicode font if needed
    if font_path:
        pdf.add_font(font_name, '', font_path, uni=True)
    pdf.set_font(font_name, size=14)
    pdf.cell(200, 10, txt=t["title"], ln=True, align="C")
    pdf.ln(10)

    pdf.set_font(font_name, size=12)
    for key in ["name", "age", "bp", "chol", "max_hr", "ecg", "risk", "disease"]:
        value = result["risk"] if key == "risk" else result["disease"] if key == "disease" else eval(key)
        pdf.cell(200, 10, txt=f"{t[key]}: {value}", ln=True)

    filename = f"{name}_report.pdf"
    pdf.output(filename)
    return filename
