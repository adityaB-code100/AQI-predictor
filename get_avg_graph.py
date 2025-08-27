import plotly.graph_objects as go
from pymongo import MongoClient

def get_city_monthly_aqi(city, uri="mongodb://localhost:27017/", db_name="AQI_Project", collection_name="monthly_aqi"):
    # Connect to MongoDB
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    result = {}

    # Fetch all monthly documents
    for doc in collection.find():
        month = doc.get("month")
        if city in doc:
            result[month] = doc[city]
    print(result)
    return result



# import plotly.offline as pyo

# def plot_monthly_aqi(city: str):
#     monthly_aqi = get_city_monthly_aqi(city)
#     sorted_data = dict(sorted(monthly_aqi.items(), key=lambda x: x[0]))
#     months = list(sorted_data.keys())
#     values = list(sorted_data.values())

#     if not values:
#         return "<div>No AQI data available for this city</div>"

#     # Convert YYYY-MM → month abbreviation
#     month_labels = [m.split("-")[1] for m in months]  # '2025-08' → '08'
#     month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
#     month_labels = [month_names[int(m)-1] for m in month_labels]

#     fig = go.Figure(
#         data=[go.Bar(
#             x=month_labels,
#             y=values,
#             marker=dict(color="#2563EB", line=dict(color="black", width=1)),
#             text=[f"{v:.1f}" for v in values],
#             textposition="outside"
#         )]
#     )

#     # Layout (matching forecast chart size)
#     fig.update_layout(
#         title=dict(
#             text=f"📊 Monthly Average AQI - {city}",
#             x=0.5,
#             font=dict(size=20, family="Arial, sans-serif", color="#111827")
#         ),
#         xaxis=dict(title="Month", tickfont=dict(size=12, color="#374151")),
#         yaxis=dict(title="AQI", range=[0, max(values) + 20],
#                    gridcolor="rgba(0,0,0,0.05)", tickfont=dict(size=12, color="#374151")),
#         plot_bgcolor="white",
#         paper_bgcolor="white",
#         margin=dict(l=40, r=20, t=50, b=60),
#         height=300,   # <-- SAME size as forecast graph
#         bargap=0.3,
#         hoverlabel=dict(
#             bgcolor="white",
#             font_size=13,
#             font_family="Arial"
#         )
#     )

#     return pyo.plot(
#         fig,
#         include_plotlyjs=False,
#         output_type="div",
#         config={"displayModeBar": False}
#     )


# import plotly.graph_objs as go
# import plotly.offline as pyo

# def get_aqi_color(aqi):
#     """Return CPCB color for given AQI value."""
#     if aqi <= 50:
#         return "#00E400"   # Good
#     elif aqi <= 100:
#         return "#9CFF9C"   # Satisfactory
#     elif aqi <= 200:
#         return "#FFFF00"   # Moderate
#     elif aqi <= 300:
#         return "#FF7E00"   # Poor
#     elif aqi <= 400:
#         return "#FF0000"   # Very Poor
#     else:
#         return "#7E0023"   # Severe

# def plot_monthly_aqi(city: str):
#     monthly_aqi = get_city_monthly_aqi(city)
#     sorted_data = dict(sorted(monthly_aqi.items(), key=lambda x: x[0]))
#     months = list(sorted_data.keys())
#     values = list(sorted_data.values())

#     if not values:
#         return "<div class='text-gray-500 italic'>No AQI data available for this city</div>"

#     # Convert YYYY-MM → month abbreviation
#     month_labels = [m.split("-")[1] for m in months]
#     month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
#     month_labels = [month_names[int(m)-1] for m in month_labels]

#     # Assign CPCB colors to each bar
#     bar_colors = [get_aqi_color(v) for v in values]

#     # Create bar chart
#     fig = go.Figure(
#         data=[go.Bar(
#             x=month_labels,
#             y=values,
#             marker=dict(color=bar_colors, line=dict(color="rgba(0,0,0,0.3)", width=1)),
#             text=[f"{v:.0f}" for v in values],
#             textposition="outside",
#             hovertemplate="Month: %{x}<br>AQI: %{y}<extra></extra>"
#         )]
#     )

#     # Layout styling
#     fig.update_layout(
#         title=dict(
#             text=f"📊 Monthly Average AQI - {city}",
#             x=0.5,
#             font=dict(size=20, family="Arial, sans-serif", color="#111827")
#         ),
#         xaxis=dict(
#             title="Month",
#             tickfont=dict(size=12, color="#374151"),
#             showgrid=False,
#             zeroline=False
#         ),
#         yaxis=dict(
#             title="AQI",
#             gridcolor="rgba(0,0,0,0.05)",
#             tickfont=dict(size=12, color="#374151"),
#             zeroline=False
#         ),
#         plot_bgcolor="white",
#         paper_bgcolor="white",
#         margin=dict(l=40, r=20, t=60, b=60),
#         height=300,   # same size as forecast chart
#         bargap=0.25,
#         hoverlabel=dict(
#             bgcolor="white",
#             bordercolor="#2563EB",
#             font_size=13,
#             font_family="Arial"
#         ),
#         transition=dict(duration=500, easing="cubic-in-out")
#     )

#     return pyo.plot(
#         fig,
#         include_plotlyjs=False,
#         output_type="div",
#         config={"displayModeBar": False, "responsive": True}
#     )
import plotly.graph_objs as go
import plotly.offline as pyo

def get_aqi_color(aqi: int) -> str:
    """Return CPCB color for given AQI value."""
    if aqi <= 50:
        return "#00E400"   # Good
    elif aqi <= 100:
        return "#9CFF9C"   # Satisfactory
    elif aqi <= 200:
        return "#FFFF00"   # Moderate
    elif aqi <= 300:
        return "#FF7E00"   # Poor
    elif aqi <= 400:
        return "#FF0000"   # Very Poor
    else:
        return "#7E0023"   # Severe


def plot_monthly_aqi(city: str):
    monthly_aqi = get_city_monthly_aqi(city)
    sorted_data = dict(sorted(monthly_aqi.items(), key=lambda x: x[0]))
    months = list(sorted_data.keys())
    values = list(sorted_data.values())

    if not values:
        return "<div class='text-gray-500 italic'>No AQI data available for this city</div>"

    # Convert YYYY-MM → month abbreviation
    month_labels = [m.split("-")[1] for m in months]
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    month_labels = [month_names[int(m)-1] for m in month_labels]

    # Assign CPCB colors to each bar
    bar_colors = [get_aqi_color(v) for v in values]

    # Create bar chart
    fig = go.Figure(
        data=[go.Bar(
            x=month_labels,
            y=values,
            marker=dict(color=bar_colors, line=dict(color="rgba(0,0,0,0.3)", width=1)),
            text=[f"{v:.0f}" for v in values],
            texttemplate="%{text}",
            textposition="auto",   # auto = smart inside/outside
            insidetextanchor="end",
            textfont=dict(color="black"),  # default for inside
            hovertemplate="Month: %{x}<br>AQI: %{y}<extra></extra>"
        )]
    )

    # Layout styling
    fig.update_layout(
        title=dict(
            text=f"📊 Monthly Average AQI - {city}",
            x=0.5,
            font=dict(size=20, family="Arial, sans-serif", color="#111827")
        ),
        xaxis=dict(
            title="Month",
            tickfont=dict(size=12, color="#374151"),
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title="AQI",
            gridcolor="rgba(0,0,0,0.05)",
            tickfont=dict(size=12, color="#374151"),
            zeroline=False
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=80, b=60),  # extra top for labels
        height=300,   # matches forecast chart height
        bargap=0.25,
        hoverlabel=dict(
            bgcolor="lavender",
            bordercolor="#000000",
            font_size=13,
            font_family="Arial"
        ),
        uniformtext=dict(minsize=10, mode="show"),
        transition=dict(duration=500, easing="cubic-in-out")
    )

    # Make bars responsive
    return pyo.plot(
        fig,
        include_plotlyjs=False,
        output_type="div",
        config={"displayModeBar": False, "responsive": True}
    )
