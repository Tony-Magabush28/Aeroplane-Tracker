from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime  # ✅ Required for 'now'

app = Flask(__name__)
API_URL = "https://opensky-network.org/api/states/all"

# ✅ Inject 'now' into all templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

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

@app.route('/flight-data')
def flight_data():
    query = request.args.get('query', '').strip().upper()
    data = None
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            flights = response.json().get('states', [])
            for flight in flights:
                icao24 = flight[0].upper()
                callsign = (flight[1] or '').strip().upper()
                if query == icao24 or query == callsign:
                    data = {
                        'icao24': icao24,
                        'callsign': callsign,
                        'latitude': flight[6],
                        'longitude': flight[5],
                    }
                    break
    except:
        pass
    return jsonify(data or {})

@app.route('/all-flights')
def all_flights():
    # Mock data for testing when OpenSky is down
    flights_data = [
        {
            'icao24': '3C4B26',
            'callsign': 'DLH123',
            'latitude': 48.3538,
            'longitude': 11.7861,
            'origin_country': 'Germany'
        },
        {
            'icao24': '4BA873',
            'callsign': 'BAW456',
            'latitude': 51.4700,
            'longitude': -0.4543,
            'origin_country': 'United Kingdom'
        },
        {
            'icao24': 'AAA111',
            'callsign': 'AFR789',
            'latitude': 48.8566,
            'longitude': 2.3522,
            'origin_country': 'France'
        }
    ]
    return jsonify(flights_data)


@app.route('/map')
def map_view():
    return render_template('all_flights.html')

if __name__ == '__main__':
    app.run(debug=True)

