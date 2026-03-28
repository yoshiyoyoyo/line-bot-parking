import httpx
import math
from typing import List, Dict, Optional
import os

TOKEN_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"

CITIES = [
    ("Keelung",          25.06, 25.22, 121.62, 121.83),
    ("Hsinchu",          24.76, 24.87, 120.92, 121.07),
    ("Chiayi",           23.43, 23.52, 120.39, 120.54),
    ("Taipei",           24.96, 25.21, 121.50, 121.67),
    ("Taoyuan",          24.55, 25.08, 120.97, 121.46),
    ("Taichung",         24.01, 24.43, 120.51, 121.10),
    ("Tainan",           22.84, 23.48, 120.06, 120.78),
    ("Kaohsiung",        22.44, 23.16, 120.24, 120.73),
    ("NewTaipei",        24.59, 25.30, 121.20, 122.03),
    ("HsinchuCounty",    24.44, 25.06, 120.78, 121.42),
    ("MiaoliCounty",     24.10, 24.70, 120.63, 121.25),
    ("ChanghuaCounty",   23.82, 24.18, 120.32, 120.73),
    ("NantouCounty",     23.50, 24.25, 120.52, 121.47),
    ("YunlinCounty",     23.50, 23.82, 120.10, 120.73),
    ("ChiayiCounty",     23.14, 23.72, 120.10, 120.89),
    ("PingtungCounty",   21.90, 22.84, 120.42, 121.00),
    ("YilanCounty",      24.30, 24.99, 121.39, 121.97),
    ("HualienCounty",    23.16, 24.47, 121.24, 121.86),
    ("TaitungCounty",    22.22, 23.16, 120.74, 121.52),
]

def detect_city(lat: float, lon: float) -> str:
    for name, lat_min, lat_max, lon_min, lon_max in CITIES:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return name
    return "Taipei"

_token_cache = {}

async def get_tdx_token(client_id: str, client_secret: str) -> Optional[str]:
    global _token_cache
    client_id = client_id.strip('"').strip("'")
    client_secret = client_secret.strip('"').strip("'")
    
    if client_id in _token_cache:
        return _token_cache[client_id]
        
    async with httpx.AsyncClient() as client:
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
        try:
            response = await client.post(TOKEN_URL, data=data)
            response.raise_for_status()
            token = response.json().get("access_token")
            _token_cache[client_id] = token
            return token
        except Exception as e:
            print(f"Error fetching TDX token: {e}")
            return None


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Haversine formula
    R = 6371e3
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2) * math.sin(delta_phi/2) + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda/2) * math.sin(delta_lambda/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


async def get_nearby_parking(lat: float, lon: float, client_id: str, client_secret: str, radius: int = 500) -> List[Dict]:
    token = await get_tdx_token(client_id, client_secret)
    if not token:
        return []

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Encoding": "gzip",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            # 1. Fetch static data via NearBy API (Advanced v1)
            static_url = "https://tdx.transportdata.tw/api/advanced/v1/Parking/OffStreet/CarPark/NearBy"
            params = {
                "$spatialFilter": f"nearby({lat}, {lon}, {radius})",
                "$format": "JSON"
            }
            static_res = await client.get(static_url, headers=headers, params=params)
            static_res.raise_for_status()
            raw_data = static_res.json()
            
            static_data = raw_data if isinstance(raw_data, list) else raw_data.get('CarParks', [])
            if not static_data:
                return []

            parking_spaces = {}
            for p in static_data:
                pid = p.get('CarParkID')
                if not pid:
                    continue
                plat = p.get('CarParkPosition', {}).get('PositionLat')
                plon = p.get('CarParkPosition', {}).get('PositionLon')
                name = p.get('CarParkName', {}).get('Zh_tw', 'Unknown')
                address = p.get('Address', '無地址')
                if isinstance(address, dict):
                    address = address.get('Zh_tw', '')
                
                dist = calculate_distance(lat, lon, plat, plon) if plat and plon else float('inf')
                
                parking_spaces[pid] = {
                    "id": pid,
                    "name": name,
                    "address": address,
                    "lat": plat,
                    "lon": plon,
                    "distance": int(dist),
                    "available_spaces": -1,
                    "total_spaces": -1
                }

            # 2. Fetch dynamic data (Availability) using boundary detection
            city = detect_city(lat, lon)
            cities_to_try = [city]
            if city == "Taipei":
                cities_to_try.append("NewTaipei")
            elif city == "NewTaipei":
                cities_to_try.append("Taipei")

            for c in cities_to_try:
                dynamic_url = f"https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/City/{c}"
                dynamic_res = await client.get(dynamic_url, headers=headers, params={"$format": "JSON"})
                if dynamic_res.status_code == 200:
                    avail_raw = dynamic_res.json()
                    dynamic_data = avail_raw if isinstance(avail_raw, list) else avail_raw.get('ParkingAvailabilities', [])
                    for d in dynamic_data:
                        pid = d.get('CarParkID')
                        if pid in parking_spaces:
                            av = d.get('AvailableSpaces', -1)
                            parking_spaces[pid]['available_spaces'] = av
                            parking_spaces[pid]['total_spaces'] = d.get('TotalSpaces', -1)
                            
            # 3. Format and sort by distance
            results = list(parking_spaces.values())
            results.sort(key=lambda x: x['distance'])
            
            return results[:10]  # LINE carousel max is 10
            
        except Exception as e:
            print(f"Error fetching parking data: {e}")
            return []
