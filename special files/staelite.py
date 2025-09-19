import ee
import geemap

# Initialize Earth Engine
ee.Initialize()

# Define location (replace with village coordinates: Selu or Kurla)
region = ee.Geometry.Point([77.1, 18.8])  # Example: Selu, Parbhani

# Load Sentinel-5P NO2 dataset
dataset = ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_NO2') \
            .select('NO2_column_number_density') \
            .filterDate('2025-09-01', '2025-09-18') \
            .filterBounds(region)

# Compute mean NO2
mean_NO2 = dataset.mean()

# Create interactive map
Map = geemap.Map()
Map.centerObject(region, 8)

# Add layer
vis_params = {
    'min': 0,
    'max': 0.0002,
    'palette': ['blue', 'green', 'yellow', 'red']
}
Map.addLayer(mean_NO2, vis_params, 'Mean NO2 (Sep 2025)')
Map.addLayer(region, {'color': 'black'}, 'Village Location')

# Display
Map
