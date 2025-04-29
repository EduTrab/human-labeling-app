# utils/streetview/geocode.py
import streamlit as st
import requests
import random
from data.cities_coordinates import city_coordinates  # <— correct import

MAPS_API_KEY = st.secrets.get("google_maps_api_key", "")

def geocode_city_to_candidates(city_name):
    if not city_name or not MAPS_API_KEY:
        return []
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": city_name, "key": MAPS_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=5).json()
    except Exception:
        return []
    candidates = []
    for r in resp.get("results", []):
        loc = r["geometry"]["location"]
        candidates.append({
            "description": r.get("formatted_address", city_name),
            "lat": loc["lat"],
            "lng": loc["lng"]
        })
    return candidates

def random_location(fallback_coords=None):
    """
    Returns a perturbed lat/lon:
    - fallback_coords if given
    - else pick a random city
    - always add slight random offset (~1km)
    """
    if fallback_coords:
        base_lat, base_lon = fallback_coords
    else:
        base_lat, base_lon = random.choice(city_coordinates)

    perturb_lat = random.uniform(-0.009, 0.009)
    perturb_lon = random.uniform(-0.009, 0.009)

    return base_lat + perturb_lat, base_lon + perturb_lon
