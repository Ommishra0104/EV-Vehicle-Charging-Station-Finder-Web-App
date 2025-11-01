# Week-1
Electric Vehicle Charging Station Finder

The EV Charging Station Finder is a Python + Flask-based web application designed to help electric vehicle (EV) users easily locate the nearest charging stations.
By entering either an address or latitude and longitude coordinates, users can instantly view nearby stations along with an interactive map built using Folium.

🌍 Project Overview

As the number of electric vehicles increases, the availability and accessibility of charging stations have become a growing concern.
This project provides a simple and smart solution — a web platform that uses AI and geospatial analysis to find the nearest EV charging points based on user location.

Users can:

Input their address or GPS coordinates

View the top nearest charging stations

See an interactive map showing station locations and distances

🧠 Features

✅ Search by address or latitude/longitude
✅ Displays the k-nearest EV charging stations
✅ Shows station details like:

Station Name

Street Address

City

Distance (in km)

Available Charger Levels (Level 1, Level 2, DC Fast)

✅ Interactive Folium Map visualization
✅ Clean and responsive web interface

🛠️ Technologies Used
Category	Tools / Libraries
Backend	Python, Flask
Data Handling	Pandas
Mapping & Geolocation	Folium, Geopy
Frontend	HTML, CSS
Machine Learning (Spatial)	scikit-learn (Nearest Neighbors)
📁 Folder Structure
EV_VEHICLES/
│
├── app.py                        # Flask main application
├── main.py                       # Core logic for data handling and nearest station search
├── Electric_Vehicle_Charging_Stations.csv  # Dataset file
│
├── templates/
│   ├── index.html                # Homepage - input form
│   └── results.html              # Result and map display
│
└── static/
    └── style.css                 # Website styling

⚙️ How to Run Locally
1️⃣ Clone the Repository
git clone https://github.com/your-username/EV-Charging-Station-Finder.git
cd EV-Charging-Station-Finder

2️⃣ Create a Virtual Environment
python -m venv ev_env
ev_env\Scripts\activate       # (Windows)

3️⃣ Install Dependencies
pip install flask pandas geopy folium scikit-learn

4️⃣ Run the Application
python app.py

5️⃣ Open in Browser

Visit → http://127.0.0.1:5000

📊 Dataset Information

The project uses a dataset named Electric_Vehicle_Charging_Stations.csv,
which contains real-world EV charging locations with attributes like:

Station Name

Street Address

City

Latitude & Longitude (georeferenced)

Charger Levels (Level 1, Level 2, DC Fast)

🚀 Future Enhancements

Add real-time availability of charging ports

Integrate GPS-based auto-location detection

Include filters (by city, distance, charger type)

Add user login to save favorite stations

Deploy app online (Render / PythonAnywhere / AWS)

👨‍💻 Author

Om Mishra
B.Tech (ECE) | Developer & Innovator
💡 Passionate about EV technology, AI, and smart city solutions..
