def filter_off(pollutants: dict) -> dict:
    required_keys = {
        "PM2.5": "PM₂.₅",
        "PM10": "PM₁₀",
        "NO2": "NO₂",
        "SO2": "SO₂",
        "Ozone": "O₃",
        "CO (mg/m³)": "CO",   # match your key name
        "NH3": "NH₃",
        "Pb": "Pb"
    }

    # keep only those pollutants which exist in data
    return {required_keys[k]: pollutants[k] for k in required_keys if k in pollutants}
