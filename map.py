import requests

def get_boundary_data(location, api_key):
    url = f"http://api.map.baidu.com/place/v2/search?query={location}&region=呼和浩特&output=json&ak={api_key}"
    response = requests.get(url)
    data = response.json()
    if 'results' in data and len(data['results']) > 0:
        result = data['results'][0]
        return result['location']
    return None

api_key = "YOUR_BAIDU_MAP_API_KEY"  # 替换为你的百度地图 API key
location1 = "社区1名称"
location2 = "社区2名称"

coords1 = get_boundary_data(location1, api_key)
coords2 = get_boundary_data(location2, api_key)

print(coords1)
print(coords2)
