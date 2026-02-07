# distance.py
from math import radians, sin, cos, sqrt, atan2
import requests, time

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjhmZjFiMWI2ZTI0MjQxNTE4MGZlMDEzYmRjYTkxYzQxIiwiaCI6Im11cm11cjY0In0="

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


def driving_distance(lat1, lon1, lat2, lon2):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": [
            [lon1, lat1],
            [lon2, lat2]
        ]
    }

    res = requests.post(url, json=body, headers=headers)
    data = res.json()

    if "routes" not in data:
        raise Exception(f"ORS error: {data}")
    
    time.sleep(2) # tránh rate limit
    
    route = data["routes"][0]
    distance_km = route["summary"]["distance"] / 1000
    duration_s = route["summary"]["duration"]

    return distance_km, duration_s


def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m} phút {s} giây"