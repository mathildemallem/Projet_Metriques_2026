import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("hello.html")

# Déposez votre code à partir d'ici :

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.get("/paris")
def api_paris():
    url = "https://api.open-meteo.com/v1/forecast?latitude=48.8566&longitude=2.3522&hourly=temperature_2m"
    response = requests.get(url, timeout=15)
    data = response.json()

    times = data.get("hourly", {}).get("time", [])
    temps = data.get("hourly", {}).get("temperature_2m", [])

    n = min(len(times), len(temps))
    result = [{"datetime": times[i], "temperature_c": temps[i]} for i in range(n)]
    return jsonify(result)

# -------- Atelier (option 1 : répartition vent) --------
@app.get("/marseille_vent")
def api_marseille_vent():
    url = "https://api.open-meteo.com/v1/forecast?latitude=43.2965&longitude=5.3698&hourly=wind_speed_10m"
    response = requests.get(url, timeout=15)
    data = response.json()

    speeds = data.get("hourly", {}).get("wind_speed_10m", [])

    bins = {
        "Faible (0–15 km/h)": 0,
        "Modéré (15–30 km/h)": 0,
        "Fort (30–50 km/h)": 0,
        "Très fort (50+ km/h)": 0
    }

    for s in speeds:
        try:
            v = float(s)
        except (TypeError, ValueError):
            continue

        if v < 15:
            bins["Faible (0–15 km/h)"] += 1
        elif v < 30:
            bins["Modéré (15–30 km/h)"] += 1
        elif v < 50:
            bins["Fort (30–50 km/h)"] += 1
        else:
            bins["Très fort (50+ km/h)"] += 1

    return jsonify([{"categorie": k, "count": v} for k, v in bins.items()])

# -------- Atelier (option 2 : vent actuel pour Gauge) --------
@app.get("/marseille_wind_now")
def api_marseille_wind_now():
    url = "https://api.open-meteo.com/v1/forecast?latitude=43.2965&longitude=5.3698&current=wind_speed_10m"
    response = requests.get(url, timeout=15)
    data = response.json()

    speed = data.get("current", {}).get("wind_speed_10m", None)

    return jsonify({
        "city": "Marseille",
        "metric": "wind_speed_10m",
        "unit": "km/h",
        "value": speed
    })

@app.route("/atelier")
def atelier():
    return render_template("atelier.html")

@app.route("/rapport")
def mongraphique():
    return render_template("graphique.html")

@app.route("/histogramme")
def monhistogramme():
    return render_template("histogramme.html")

# Ne rien mettre après ce commentaire
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)