def predict_risk(age, bp, chol, max_hr, ecg):
    score = 0
    if age > 50: score += 1
    if bp > 130: score += 1
    if chol > 200: score += 1
    if max_hr < 100: score += 1
    if ecg == "Abnormal": score += 1

    if score >= 4:
        risk = "High Risk"
        disease = "Coronary Artery Disease"
    elif score == 3:
        risk = "Moderate Risk"
        disease = "Arrhythmia"
    elif score == 2:
        risk = "Low Risk"
        disease = "Heart Hole (Congenital)"
    else:
        risk = "Very Low Risk"
        disease = "Healthy"

    return {"risk": risk, "disease": disease, "score": score}
