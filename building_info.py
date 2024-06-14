import geopandas as gpd
import json

# 读取地理数据
gdf = gpd.read_file('data.geojson')

# 打开并读取GeoJSON文件
with open('data.geojson', 'r') as file:
    geojson_data = json.load(file)

# 手动添加建筑物信息，使用 `id` 作为键
building_info_dict = {
    1: {'name': 'Building A', 'description': 'Description of Building A', 'other_attribute': 'Other value A'},
    2: {'name': 'Building B', 'description': 'Description of Building B', 'other_attribute': 'Other value B'},
    # 添加更多建筑物信息
}

# 创建空列
gdf['name'] = None
gdf['description'] = None
gdf['other_attribute'] = None

# 根据 `id` 匹配并添加建筑物信息
for feature in geojson_data['features']:
    feature_id = feature['id']
    if feature_id in building_info_dict:
        gdf.loc[gdf.index == feature_id, 'name'] = building_info_dict[feature_id]['name']
        gdf.loc[gdf.index == feature_id, 'description'] = building_info_dict[feature_id]['description']
        gdf.loc[gdf.index == feature_id, 'other_attribute'] = building_info_dict[feature_id]['other_attribute']

# 显示添加后的 GeoDataFrame
print(gdf)
