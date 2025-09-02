
import pandas as pd
import folium
import geopandas as gpd
from geopy.geocoders import Nominatim
import os
import geopandas as gpd

# current_dir = os.path.dirname(__file__)  # folder of processing.py
# geojson_path = os.path.join(current_dir, "india_district.geojson")
# gdf = gpd.read_file(geojson_path)

# ----------------- CONFIG -----------------
geojson_path = "india_district.geojson"
geolocator = Nominatim(user_agent="aqi_map")


def mapgenerator(date,aqi):
    # Multiple AQI locations
    aqi_data = [
    {'village': "NANDED", 'lat': 18.916670, 'lon': 77.500000, 'aqi': aqi['Nanded']},
    {'village': "PUNE", 'lat': 18.520430, 'lon': 73.856743, 'aqi': aqi['Pune']},
    {'village': "MUMBAI", 'lat': 19.076090, 'lon': 72.877426, 'aqi': aqi['Mumbai']},
    {'village': "NAGPUR", 'lat': 21.145800, 'lon': 79.088200, 'aqi': aqi['Nagpur']},
    {'village': "NASHIK", 'lat': 20.011000, 'lon': 73.790000, 'aqi': aqi['Nashik']}
    ]


    if aqi_data:
        # Map villages to AQI
        village_aqi_map = {d['village'].lower(): d['aqi'] for d in aqi_data}

        # AQI color function
        def get_aqi_color(aqi):
            if aqi <= 50:
                return "#22C55E"
            elif aqi <= 100:
                return "#FACC15"
            elif aqi <= 150:
                return "#F97316"
            elif aqi <= 200:
                return "#EF4444"
            elif aqi <= 300:
                return "#9333EA"
            else:
                return "#111827"

        # Read GeoJSON districts
        gdf = gpd.read_file(geojson_path)

        # Map district → highest AQI among villages in that district
        district_aqi_map = {}
        for idx, row in gdf.iterrows():
            district_name = row['DISTRICT'].lower()
            for v in village_aqi_map:
                if v in district_name:  # crude match; improve if needed
                    district_aqi_map[district_name] = max(
                        district_aqi_map.get(district_name, 0),
                        village_aqi_map[v]
                    )

        # Create map
        m = folium.Map(location=[20, 75], zoom_start=5)

        # Style districts based on AQI
        def style_function(feature):
            dist_name = feature["properties"]["DISTRICT"].lower()
            if dist_name in district_aqi_map:
                color = get_aqi_color(district_aqi_map[dist_name])
                return {"fillColor": color, "color": "transparent", "weight": 0, "fillOpacity": 0.6}
            else:
                return {"fillColor": "transparent", "color": "transparent", "weight": 0}

        folium.GeoJson(geojson_path, style_function=style_function).add_to(m)

        # Add markers for each village
        bounds = []
        for loc in aqi_data:
            folium.CircleMarker(
                location=[loc['lat'], loc['lon']],
                radius=8,
                color=get_aqi_color(loc['aqi']),
                fill=True,
                fill_opacity=0.01,
                popup=f"{loc['village']}: AQI {loc['aqi']}"
            ).add_to(m)
            bounds.append([loc['lat'], loc['lon']])

        # Auto zoom
        m.fit_bounds(bounds)

        # -------- Inject JS for click event --------
        map_id = m.get_name()
        click_js = f"""
            <script>
                {map_id}.on('click', function(e) {{
                    var lat = e.latlng.lat.toFixed(6);
                    var lng = e.latlng.lng.toFixed(6);

                    // Show coordinates in alert
                    alert("Latitude: " + lat + "\\nLongitude: " + lng);

                    // Send to Flask backend
                    fetch('/p', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{ latitude: lat, longitude: lng }})
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        console.log("Server response:", data);
                    }})
                    .catch(error => {{
                        console.error("Error:", error);
                    }});
                }});
            </script>
        """
        m.get_root().html.add_child(folium.Element(click_js))
        print("map generated")
        m.save(f"static/map{date}.html")
        #return m
        return m._repr_html_()

