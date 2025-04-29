# utils/streetview/fetch.py

import os
import time
import random
import logging
import streamlit as st

from streetview import search_panoramas, get_panorama_meta, get_streetview
from configs.config import SAVE_DIR
from data.cities_coordinates import city_coordinates
from utils.streetview.geocode import random_location  # <-- Correct random_location imported

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def generate_city_perturbations(base_lat, base_lon, n, radius_km=1.0):
    """
    Return n random (lat,lon) within +/- radius_km of (base_lat, base_lon).
    """
    max_off = radius_km * 0.009   # ~ degrees per km
    return [
        (
            base_lat + random.uniform(-max_off, max_off),
            base_lon + random.uniform(-max_off, max_off),
        )
        for _ in range(n)
    ]

def search_and_download_random(idx, coords=None, max_retries=5):
    for attempt in range(1, max_retries + 1):
        lat, lon = random_location(coords)
        logger.info(f"Searching panoramas at {lat:.5f},{lon:.5f} (idx={idx}, attempt={attempt})")
        try:
            panos = search_panoramas(lat=lat, lon=lon)
            if not panos:
                raise RuntimeError("no panoramas found")

            pano_id = panos[0].pano_id

            img = get_streetview(pano_id=pano_id, api_key=st.secrets["google_maps_api_key"])
            img_path = os.path.join(SAVE_DIR, f"{idx}.png")
            img.save(img_path, "PNG")

            meta = get_panorama_meta(pano_id=pano_id, api_key=st.secrets["google_maps_api_key"])
            json_path = os.path.join(SAVE_DIR, f"{idx}.json")
            with open(json_path, "w") as jf:
                jf.write(meta.json())

            logger.info(f"✅ Downloaded {img_path} + {json_path}")
            return img_path, json_path

        except Exception as e:
            logger.warning(f"❌ attempt {attempt} for idx {idx} failed: {e}")
            time.sleep(0.2)

    logger.error(f"🔴 All {max_retries} attempts failed for idx {idx}; skipping")
    return None, None
