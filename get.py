import geopandas as gpd
data = gpd.read_file('caijing.geojson')
data.to_file('caijing', driver='ESRI Shapefile', encoding='utf-8')