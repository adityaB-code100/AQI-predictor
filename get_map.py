
# import pandas as pd
# import folium
# import geopandas as gpd
# from geopy.geocoders import Nominatim

# # ----------------- CONFIG -----------------
# geojson_path = "india_district.geojson"
# geolocator = Nominatim(user_agent="aqi_map")


# def mapgenerator(aqi):
#     # Multiple AQI locations
#     aqi_data = [
#         {'village': "NANDED", 'lat': 18.916670, 'lon': 77.500000, 'aqi': aqi['VillageA']},
#         {'village': "PUNE", 'lat': 18.520430, 'lon': 73.856743, 'aqi': aqi['VillageB']},
#         {'village': "MUMBAI", 'lat': 19.076090, 'lon': 72.877426, 'aqi': 200}
#     ]

#     if aqi_data:
#         # Map villages to AQI
#         village_aqi_map = {d['village'].lower(): d['aqi'] for d in aqi_data}

#         # AQI color function
#         def get_aqi_color(aqi):
#             if aqi <= 50:
#                 return "green"
#             elif aqi <= 100:
#                 return "yellow"
#             elif aqi <= 200:
#                 return "orange"
#             elif aqi <= 300:
#                 return "red"
#             else:
#                 return "maroon"

#         # Read GeoJSON districts
#         gdf = gpd.read_file(geojson_path)

#         # Map district → highest AQI among villages in that district
#         district_aqi_map = {}
#         for idx, row in gdf.iterrows():
#             district_name = row['DISTRICT'].lower()
#             for v in village_aqi_map:
#                 if v in district_name:  # crude match; improve if needed
#                     # If multiple villages per district, take max AQI
#                     district_aqi_map[district_name] = max(
#                         district_aqi_map.get(district_name, 0),
#                         village_aqi_map[v]
#                     )

#         # Create map (temporary center, will adjust with fit_bounds)
#         m = folium.Map(location=[20, 75], zoom_start=5)

#         # Style districts based on AQI
#         def style_function(feature):
#             dist_name = feature["properties"]["DISTRICT"].lower()
#             if dist_name in district_aqi_map:
#                 color = get_aqi_color(district_aqi_map[dist_name])
#                 return {"fillColor": color, "color": "transparent", "weight": 0, "fillOpacity": 0.6}
#             else:
#                 return {"fillColor": "transparent", "color": "transparent", "weight": 0}

#         folium.GeoJson(geojson_path, style_function=style_function).add_to(m)

#         # Add markers for each village
#         bounds = []
#         for loc in aqi_data:
#             folium.CircleMarker(
#                 location=[loc['lat'], loc['lon']],
#                 radius=8,
#                 color=get_aqi_color(loc['aqi']),
#                 fill=True,
#                 fill_opacity=0.01,
#                 popup=f"{loc['village']}: AQI {loc['aqi']}"
#             ).add_to(m)
#             bounds.append([loc['lat'], loc['lon']])

#         # Auto zoom to include all villages
#         m.fit_bounds(bounds)

#         # # Coordinate display
#         # map_id = m.get_name()
#         # click_js = f"""
#         #     <style>
#         #         .coord-box {{
#         #             background: white;
#         #             padding: 8px;
#         #             border-radius: 4px;
#         #             font-size: 14px;
#         #             box-shadow: 0 0 5px rgba(0,0,0,0.3);
#         #         }}
#         #     </style>
#         #     <script>
#         #         var coordDiv = L.control({{position: 'bottomleft'}});
#         #         coordDiv.onAdd = function (map) {{
#         #             this._div = L.DomUtil.create('div', 'coord-box');
#         #             this.update();
#         #             return this._div;
#         #         }};
#         #         coordDiv.update = function (lat, lng) {{
#         #             this._div.innerHTML = lat && lng 
#         #                 ? "<b>Latitude:</b> " + lat + "<br><b>Longitude:</b> " + lng
#         #                 : "Click on the map to get coordinates";
#         #         }};
#         #         coordDiv.addTo({map_id});

#         #         {map_id}.on('click', function(e) {{
#         #             var lat = e.latlng.lat.toFixed(6);
#         #             var lng = e.latlng.lng.toFixed(6);
#         #             coordDiv.update(lat, lng);
#         #         }});
#         #     </script>
#         # """

#             # Flask + Folium: send clicked coords to /p
#         map_id = m.get_name()
#         click_js = f"""
#             <script>
#                 {map_id}.on('click', function(e) {{
#                     var lat = e.latlng.lat.toFixed(6);
#                     var lng = e.latlng.lng.toFixed(6);

#                     // Show in alert
#                     alert("Latitude: " + lat + "\\nLongitude: " + lng);

#                     // Send to Flask backend
#                     fetch('/p', {{
#                         method: 'POST',
#                         headers: {{
#                             'Content-Type': 'application/json'
#                         }},
#                         body: JSON.stringify({{ latitude: lat, longitude: lng }})
#                     }})
#                     .then(response => response.json())
#                     .then(data => {{
#                         console.log("Server response:", data);
#                     }})
#                     .catch(error => {{
#                         console.error("Error:", error);
#                     }});
#                 }});
#             </script>
#         """
#         m.get_root().html.add_child(folium.Element(click_js))

#     #m.get_root().html.add_child(folium.Element(click_js))

#         # Save map
#         m.save("static/Full_Final_AQI_Map_change.html")
#         print("✅ Map saved with all villages and auto-zoom")
#     else:
#         print("❌ No AQI data found to plot.")


import pandas as pd
import folium
import geopandas as gpd
from geopy.geocoders import Nominatim

# ----------------- CONFIG -----------------
geojson_path = "india_district.geojson"
geolocator = Nominatim(user_agent="aqi_map")


def mapgenerator(aqi):
    # Multiple AQI locations
    aqi_data = [
        {'village': "NANDED", 'lat': 18.916670, 'lon': 77.500000, 'aqi': aqi['VillageA']},
        {'village': "PUNE", 'lat': 18.520430, 'lon': 73.856743, 'aqi': aqi['VillageB']},
        {'village': "MUMBAI", 'lat': 19.076090, 'lon': 72.877426, 'aqi': 200}
    ]

    if aqi_data:
        # Map villages to AQI
        village_aqi_map = {d['village'].lower(): d['aqi'] for d in aqi_data}

        # AQI color function
        def get_aqi_color(aqi):
            if aqi <= 50:
                return "green"
            elif aqi <= 100:
                return "yellow"
            elif aqi <= 200:
                return "orange"
            elif aqi <= 300:
                return "red"
            else:
                return "maroon"

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
        #m.save("static/Full_Final_AQI_Map_change.html")
        #return m
        return m._repr_html_()

