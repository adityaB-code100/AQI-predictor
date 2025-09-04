import subprocess
import sys

def install_requirements():
    packages = [
        "Flask",
        "Flask-PyMongo",
        "Werkzeug",
        "pymongo",
        "twilio",
        "pandas",
        "numpy",
        "xgboost",
        "folium",
        "geopandas",
        "geopy",
        "google-generativeai",
        "plotly",
        "Flask-Mail"
    ]

    for package in packages:
        try:
            print(f"📦 Installing {package} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

if __name__ == "__main__":
    install_requirements()
