# utils/common/human_upload.py

import os
import shutil
import json
import streamlit as st
from googleapiclient.http import MediaFileUpload
from utils.common.drive_upload import (
    get_drive_service,
    ensure_drive_folder,
    drive_pool,
    DRIVE_ROOT_FOLDER_ID
)
from configs.config import HUMAN_CREATED_DIR

def find_unique_filename(base_filename, folder):
    """
    Ensure that the filename is unique in the folder by appending _reX if needed.
    """
    base_name, ext = os.path.splitext(base_filename)
    candidate = base_filename
    counter = 1
    while os.path.exists(os.path.join(folder, candidate)):
        candidate = f"{base_name}_re{counter}{ext}"
        counter += 1
    return candidate

def save_human_record(record):
    """
    Save the human-created question + image locally and upload to Google Drive.
    """
    # Safely get username immediately (avoid background thread errors)
    username = st.session_state.get("username")

    if not username:
        st.toast("⚠️ Username missing. Cannot upload.", icon="⚠️")
        return

    # 1. Find safe filenames
    base_image_name = os.path.basename(record["image_path"])
    unique_img_name = find_unique_filename(base_image_name, HUMAN_CREATED_DIR)
    img_dest = os.path.join(HUMAN_CREATED_DIR, unique_img_name)

    # Copy image locally
    shutil.copy(record["image_path"], img_dest)

    # 2. Save corresponding JSON
    unique_json_name = os.path.splitext(unique_img_name)[0] + ".json"
    json_path = os.path.join(HUMAN_CREATED_DIR, unique_json_name)

    data = {
        "question": record["question"],
        "options": record["options"],
        "correct_answer": record["correct_answer"],
        "explanation": record.get("explanation", "")
    }
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

    # 3. Async upload to Google Drive
    def task(username=username, img_dest=img_dest, json_path=json_path):
        try:
            svc = get_drive_service()

            # Create user folder
            user_folder = ensure_drive_folder(svc, f"userHR_{username}", DRIVE_ROOT_FOLDER_ID)

            # Create (or reuse) human_created subfolder
            human_folder = ensure_drive_folder(svc, "human_created", user_folder)

            # Upload image and JSON
            for local_path in (img_dest, json_path):
                media = MediaFileUpload(local_path, resumable=True)
                svc.files().create(
                    body={"name": os.path.basename(local_path), "parents": [human_folder]},
                    media_body=media,
                    fields="id"
                ).execute()

            print(f"[UPLOAD SUCCESS] {os.path.basename(img_dest)} and {os.path.basename(json_path)} uploaded.")

        except Exception as e:
            print(f"[UPLOAD FAIL] {e}")

    drive_pool.submit(task)
