import os
import json
import time
import streamlit as st

from configs.config import SAVE_DIR, ANSWERED_DIR
from data.cities_coordinates import city_coordinates
from streetview import search_panoramas, get_panorama_meta, get_streetview
from utils.common.index_utils import random_location





def download_image_maps(pano_id, idx):
    """
    Downloads a Google Street View image using the panorama ID
    and saves it along with its metadata.

    Parameters:
        pano_id (str): The panorama identifier.
        idx (int): The index to be used in the filename.

    Returns:
        tuple: (image_path, json_path)
    """
    print("[DEBUG] Using API KEY inside fetch:", st.secrets.get("google_maps_api_key"))
    try:
        image = get_streetview(pano_id=pano_id, api_key=st.secrets.get("google_maps_api_key", ""))
        image_path = os.path.join(SAVE_DIR, f"{idx}.png")
        image.save(image_path, "png")

        meta = get_panorama_meta(pano_id=pano_id, api_key=st.secrets.get("google_maps_api_key", ""))
        meta_data = {
            "pano_id": pano_id,
            "location": {"lat": meta.location.lat, "lng": meta.location.lng},
            "date": meta.date
        }
        json_path = os.path.join(SAVE_DIR, f"{idx}.json")
        with open(json_path, 'w') as f:
            json.dump(meta_data, f, indent=4)
        return image_path, json_path
    except Exception as e:
        print(f"Error downloading image or metadata for pano_id {pano_id}: {e}")
        return None, None
    






import os
import json
import time
from math import radians, cos, sin, sqrt, atan2
from typing import Tuple

import mercantile
import requests
from vt2geojson.tools import vt_bytes_to_geojson






# -----------------------------------------------------------------------------
# Utility helpers
# -----------------------------------------------------------------------------

def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great‑circle distance between two points on Earth in **meters**."""
    R = 6_371_000  # mean Earth radius in metres
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def _get(url: str, max_retries: int, headers: dict | None = None, stream: bool = False):
    """HTTP GET with basic retry/back‑off."""
    last_error: Exception | None = None
    for _ in range(max_retries):
        try:
            r = requests.get(url, headers=headers, stream=stream, timeout=15)
            r.raise_for_status()
            return r
        except Exception as exc:  # pylint: disable=broad-except
            last_error = exc
            time.sleep(1.0)
    raise RuntimeError(f"Failed after {max_retries} attempts → {url}\n{last_error}")


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------
import random
def  search_and_download_random_mly(
    indx: int =None, # for compatibility
    coords: Tuple[float, float] | None = None,
    max_retries: int = 3,
    radius_m: float=10000,
    access_token: str="MLY|23937335652558993|eb49143137817a491c1f5257340cd217" ,
    out_dir: str = SAVE_DIR,
    zoom: int = 14,
    tile_coverage: str = "mly1_public",
    tile_layer: str = "image",
) -> Tuple[str, str]:
    """Fetch **one** Mapillary image captured inside a given radius.

    Parameters
    ----------
    coords : tuple(lat, lon)
        Central point of search (WGS‑84 degrees).
    radius_m : float
        Search radius *in metres* around ``coords``. Images farther than this are ignored.
    access_token : str
        Mapillary API token.
    max_retries : int, default 3
        Attempts per network call.
    out_dir : str, default "mapillary_download"
        Directory to store the downloaded files.

    Returns
    -------
    json_path, image_path : tuple[str, str]
        Paths to the metadata JSON and JPEG respectively.

    Raises
    ------
    RuntimeError
        If no imagery is found inside the requested circle.
    """

    if coords:
        lat, lon = coords
    else:
        lat, lon = random_location()

    lat_shift = random.uniform(-0.01, 0.01)  # Adjust the range as needed
    lon_shift = random.uniform(-0.01, 0.01)  # Adjust the range as needed

    lat += lat_shift
    lon += lon_shift

    # ------------------------------------------------------------------
    # 1. Compute bounding‑box around the search circle (fast tile lookup)
    # ------------------------------------------------------------------
    deg_per_m_lat = 1.0 / 111_320  # ° per metre (lat)
    deg_per_m_lon = 1.0 / (111_320 * cos(radians(lat)))  # varies by latitude

    dlat = radius_m * deg_per_m_lat
    dlon = radius_m * deg_per_m_lon

    west, south, east, north = lon - dlon, lat - dlat, lon + dlon, lat + dlat
    tiles = list(mercantile.tiles(west, south, east, north, zoom))

    #os.makedirs(out_dir, exist_ok=True)
    indx=time.time()
    for tile in tiles:
        tile_url = (
            f"https://tiles.mapillary.com/maps/vtp/{tile_coverage}/2/"
            f"{tile.z}/{tile.x}/{tile.y}?access_token={access_token}"
        )
        vt_bytes = _get(tile_url, max_retries).content
        geojson = vt_bytes_to_geojson(
            vt_bytes, tile.x, tile.y, tile.z, layer=tile_layer
        )

        for feature in geojson["features"]:
            lng, lat_f = feature["geometry"]["coordinates"]
            if _haversine_m(lat, lon, lat_f, lng) > radius_m:
                continue  # outside circle

            # ---------- we've got our first match → download + save ----------
            image_id = feature["properties"]["id"]

            fields = "thumb_2048_url,computed_geometry,captured_at"
            graph_url = f"https://graph.mapillary.com/{image_id}?fields={fields}"
            headers = {"Authorization": f"OAuth {access_token}"}

            meta = _get(graph_url, max_retries, headers).json()
            lng_meta, lat_meta = meta["computed_geometry"]["coordinates"]

            # download JPEG
            image_path = os.path.join(out_dir, f"{indx}.jpg")
            img_resp = _get(meta["thumb_2048_url"], max_retries, stream=True)
            with open(image_path, "wb") as fp:
                for chunk in img_resp.iter_content(chunk_size=64 * 1024):
                    if chunk:
                        fp.write(chunk)

            # write JSON metadata
            json_path = os.path.join(out_dir, f"{indx}.json")
            with open(json_path, "w", encoding="utf-8") as fp:
                json.dump(
                    {   "pano_id": indx,
                        "location": {"lat": lat_meta, "lng": lng_meta},
                        "date": meta.get("captured_at"),
                    },
                    fp,
                    #ensure_ascii=False,
                    indent=4,
                )

            return  image_path, json_path  # ← RETURN ONLY ONE IMAGE / META

    # loop exited → no image found
    raise RuntimeError("No Mapillary imagery found within the specified radius.")





def search_and_download_random_maps(idx, coords=None, max_retries=10):
    """
    Attempts to find and download a random Street View image.
    Retries up to max_retries times if it cannot find a valid panorama.

    Parameters:
        idx (int): Index for naming files.
        coords (optional): Tuple of (lat, lon) to override random.
        max_retries (int): Maximum retry attempts (default is 10).
    """
    retries = 0
    while retries < max_retries:
        try:
            if coords:
                base_lat, base_lon = coords
            else:
                base_lat, base_lon = random_location()

            print(f"[CityCoord] Using lat/lon: {base_lat:.5f}, {base_lon:.5f}")
            panos = search_panoramas(lat=base_lat, lon=base_lon)
            if not panos:
                raise Exception(f"No panoramas found at {base_lat}, {base_lon}")
            pano_id = panos[0].pano_id
            return download_image_maps(pano_id, idx)
        except Exception as e:
            print(f"Exception occurred: {e}")
            retries += 1
            time.sleep(0.2)
    return None, None
