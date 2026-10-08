def calculate_heat_risk(temperature):
    if temperature > 40:
        return "High"
    elif temperature > 30:
        return "Medium"
    return "Low"