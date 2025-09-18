import plotly.graph_objs as go
import plotly.offline as pyo

def create_aqi_forecast_chart(dates, aqi_values, title="7 days Graphical AQI Forecast"):
    """
    Create an AQI forecast chart (time vs AQI) using Plotly.
    Returns an embeddable HTML <div> string for Flask/Jinja templates.
    """
    fig = go.Figure()

    # Main AQI line
    fig.add_trace(go.Scatter(
        x=dates, y=aqi_values,
        mode="lines+markers",
        name="AQI",
        line=dict(color="#2563EB", width=3),
        marker=dict(size=7, color="white", line=dict(color="#2563EB", width=2)),
        hovertemplate="Date: %{x}<br>AQI: %{y}<extra></extra>"
    ))

    # Fill under curve
    fig.add_trace(go.Scatter(
        x=dates, y=aqi_values,
        fill='tozeroy',
        mode='none',
        fillcolor="rgba(37, 99, 235, 0.15)",
        showlegend=False
    ))

    # Layout styling
    fig.update_layout(
        title=dict(
            text=f"🌍 {title}",
            x=0.5,
            xanchor="center",
            font=dict(size=20, family="Arial, sans-serif", color="#111827")
        ),
        xaxis=dict(
            title="Date",
            showgrid=False,
            tickfont=dict(size=12, color="#374151"),
            tickangle=-90   # <-- rotate labels vertically
        ),
        yaxis=dict(
            title="AQI",
            gridcolor="rgba(0,0,0,0.05)",
            zeroline=False,
            tickfont=dict(size=12, color="#374151")
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=50, b=80),  # extra bottom margin for vertical ticks
        height=300,
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Arial"
        )
    )

    # Return HTML <div> without mode bar
    return pyo.plot(
        fig,
        include_plotlyjs=False,
        output_type="div",
        config={"displayModeBar": False}
    )
