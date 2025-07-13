from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

API_URL = "https://opensky-network.org/api/states/all"

# Cache OpenSky data for 30 seconds to avoid overloading the API
app.cache = {"flights": [], "timestamp": datetime.now(timezone.utc) - timedelta(seconds=60)}


# Inject 'now' into templates for footer time
@app.context_processor
def inject_now():
    return {'now': lambda: datetime.now(timezone.utc)}


@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    error = None
    if request.method == 'POST':
        search_query = request.form.get('query').strip().upper()
        try:
            response = requests.get(API_URL, timeout=10)
            if response.status_code == 200:
                flights = response.json().get('states', [])
                for flight in flights:
                    icao24 = flight[0].upper()
                    callsign = (flight[1] or '').strip().upper()
                    if search_query == icao24 or search_query == callsign:
                        data = {
                            'icao24': icao24,
                            'callsign': callsign,
                            'origin_country': flight[2],
                            'latitude': flight[6],
                            'longitude': flight[5],
                            'altitude': flight[7],
                            'velocity': flight[9],
                            'heading': flight[10],
                        }
                        break
                if not data:
                    error = "Flight not found."
            else:
                error = "Failed to fetch data from OpenSky."
        except Exception as e:
            error = str(e)
    return render_template('index.html', data=data, error=error)


@app.route('/all-flights')
def all_flights():
    now = datetime.now(timezone.utc)

    if (now - app.cache["timestamp"]).total_seconds() > 30:
        flights_data = []
        try:
            response = requests.get(API_URL, timeout=10)
            if response.status_code == 200:
                flights = response.json().get('states', [])
                for flight in flights:
                    if flight[5] is not None and flight[6] is not None:
                        flights_data.append({
                            'icao24': flight[0].upper(),
                            'callsign': (flight[1] or '').strip(),
                            'origin_country': flight[2],
                            'longitude': flight[5],
                            'latitude': flight[6],
                            'altitude': flight[7] if flight[7] is not None else 0,
                            'velocity': flight[9] if flight[9] is not None else 0,
                            'heading': flight[10] if flight[10] is not None else 0,
                        })
            app.cache["flights"] = flights_data
            app.cache["timestamp"] = now
        except Exception as e:
            print("Error fetching OpenSky data:", e)

    return jsonify(app.cache["flights"])


@app.route('/map')
def map_view():
    return render_template('all_flights.html')


if __name__ == '__main__':
    app.run(debug=True)

