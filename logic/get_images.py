# logic/get_images.py

import os
import logging
import shutil
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.streetview.fetch import (
    search_and_download_random_mly,
    generate_city_perturbations,
)
from utils.common.index_utils import get_next_idx
from configs.config import TMP_UPLOAD_DIR

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def _clear_tmp_folder():
    shutil.rmtree(TMP_UPLOAD_DIR, ignore_errors=True)
    os.makedirs(TMP_UPLOAD_DIR, exist_ok=True)

def download_images():
    N = st.session_state.batch_size
    src = st.session_state.dataset_source

    _clear_tmp_folder()
    batch = []
    idx_start = get_next_idx()

    if src == "Local":
        available = [
            f for f in st.session_state.local_records
            if f.name not in st.session_state.processed_files
        ]
        if len(available) < N:
            st.error(f"❌ Not enough local images remaining. Please upload more.")
            return

        selected_files = available[:N]

        for i, f in enumerate(selected_files):
            new_path = os.path.join(TMP_UPLOAD_DIR, f"{idx_start+i}.png")
            with open(new_path, "wb") as w:
                w.write(f.getbuffer())
            batch.append({"image_path": new_path})

        # Mark these files as processed
        st.session_state.processed_files.update(f.name for f in selected_files)

    else:
        if src == "City" and st.session_state.city_latlon:
            base_lat, base_lon = st.session_state.city_latlon
            coords_list = generate_city_perturbations(base_lat, base_lon, N)
        else:
            coords_list = [None] * N

        logger.info(f"Downloading {N} images from {src} source.")
        with ThreadPoolExecutor(max_workers=min(5, N)) as exe:
            futures = [
                exe.submit(search_and_download_random_mly, idx_start+i, coords_list[i])
                for i in range(N)
            ]
            for fut in as_completed(futures):
                img_path, _ = fut.result()
                if img_path:
                    batch.append({"image_path": img_path})

    if not batch:
        st.error("❌ No images could be downloaded. Check your connection or API key.")
    else:
        st.session_state.current_batch = batch
        st.session_state.submitted = False

def handle_get_images():
    if st.button("Get Images"):
        with st.spinner("📥 Downloading Images..."):
            download_images()
