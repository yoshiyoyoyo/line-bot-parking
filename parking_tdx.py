import httpx
import math
from typing import List, Dict, Optional
import os

TOKEN_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
BASE_URL = "https://tdx.transportdata.tw/api/advanced/v2/Parking"


async def get_tdx_token(client_id: str, client_secret: str) -> Optional[str]:
    async with httpx.AsyncClient() as client:
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
        try:
            response = await client.post(TOKEN_URL, data=data)
            response.raise_for_status()
            return response.json().get("access_token")
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
        "Accept": "application/json"
    }

    spatial_filter = f"nearby({lat},{lon},{radius})"
    
    async with httpx.AsyncClient() as client:
        try:
            parking_spaces = {}
            cities = ["Taipei", "NewTaipei"]
            
            for city in cities:
                # 1. Fetch static data
                static_url = f"https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/CarPark/City/{city}"
                params = {
                    "$spatialFilter": spatial_filter,
                    "$format": "JSON"
                }
                
                static_res = await client.get(static_url, headers=headers, params=params)
                if static_res.status_code != 200:
                    continue
                    
                static_data = static_res.json().get('CarParks', [])

                # 2. Extract Parking IDs for dynamic data query
                for p in static_data:
                    pid = p.get('CarParkID')
                    if not pid:
                        continue
                    plat = p.get('CarParkPosition', {}).get('PositionLat')
                    plon = p.get('CarParkPosition', {}).get('PositionLon')
                    name = p.get('CarParkName', {}).get('Zh_tw', 'Unknown')
                    address = p.get('Address', '無地址')
                    
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

                # 3. Fetch dynamic data (Availability)
                dynamic_url = f"https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/City/{city}"
                dynamic_res = await client.get(dynamic_url, headers=headers, params=params)
                if dynamic_res.status_code == 200:
                    dynamic_data = dynamic_res.json().get('ParkingAvailabilities', [])
                    for d in dynamic_data:
                        pid = d.get('CarParkID')
                        if pid in parking_spaces:
                            av = d.get('AvailableSpaces', -1)
                            parking_spaces[pid]['available_spaces'] = av
                            parking_spaces[pid]['total_spaces'] = d.get('TotalSpaces', -1)
            
            # 4. Format and sort by distance
            results = list(parking_spaces.values())
            results.sort(key=lambda x: x['distance'])
            
            return results[:10]  # LINE carousel max is 10
            
        except Exception as e:
            print(f"Error fetching parking data: {e}")
            return []
