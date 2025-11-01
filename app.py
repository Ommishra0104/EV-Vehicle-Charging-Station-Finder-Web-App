# app.py
from flask import Flask, render_template, request
from markupsafe import Markup
from geopy.geocoders import Nominatim
import folium
from main import load_and_prepare, find_nearest

app = Flask(__name__)

DATA_CSV = "Electric_Vehicle_Charging_Stations.csv"
df = load_and_prepare(DATA_CSV)
print("DEBUG: loaded stations count:", len(df))   # helpful debug in console

geolocator = Nominatim(user_agent="ev_finder_app")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/results", methods=["POST"])
def results():
    address = request.form.get("address", "").strip()
    lat_input = request.form.get("latitude", "").strip()
    lon_input = request.form.get("longitude", "").strip()
    k = int(request.form.get("k", 5))

    query_lat = None
    query_lon = None
    error = None

    # prefer numeric lat/lon if provided
    if lat_input and lon_input:
        try:
            query_lat = float(lat_input)
            query_lon = float(lon_input)
        except ValueError:
            error = "Latitude/Longitude must be numeric."
    elif address:
        # geocode
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                query_lat = location.latitude
                query_lon = location.longitude
            else:
                error = f"Could not geocode address: {address}"
        except Exception as e:
            error = f"Geocoding error: {e}"
    else:
        error = "Please provide address or latitude & longitude."

    if error:
        return render_template("results.html", error=error)

    nearest = find_nearest(df, query_lat, query_lon, k=k)

    # Create folium map centered on query
    m = folium.Map(location=[query_lat, query_lon], zoom_start=13)
    folium.Marker([query_lat, query_lon], popup="Your Location", icon=folium.Icon(color="red")).add_to(m)

    for s in nearest:
        popup_html = f"<b>{s['station_name']}</b><br>{s['street_address']}<br>{s['city']}<br>Distance: {s['distance_km']} km"
        folium.Marker([s["latitude"], s["longitude"]], popup=popup_html).add_to(m)

    map_html = m._repr_html_()
    return render_template("results.html", nearest=nearest, map_html=Markup(map_html), query_lat=query_lat, query_lon=query_lon)

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True)
