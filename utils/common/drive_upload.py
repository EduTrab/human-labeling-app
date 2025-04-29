import os
import streamlit as st
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# your GDrive root
DRIVE_ROOT_FOLDER_ID = st.secrets["gdrive"]["root_folder_id"]

# Thread pool for uploads
drive_pool = ThreadPoolExecutor(max_workers=5)
user_folder_cache = {}
folder_cache_lock = Lock()

def get_drive_service():
    info = dict(st.secrets["gdrive"])
    info["private_key"] = info["private_key"].replace("\\n","\n")
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive","v3",credentials=creds)

def ensure_drive_folder(service, name, parent_id):
    q = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
    res = service.files().list(q=q, fields="files(id)").execute().get("files",[])
    if res: return res[0]["id"]
    meta = {"name":name,"mimeType":"application/vnd.google-apps.folder","parents":[parent_id]}
    return service.files().create(body=meta, fields="id").execute()["id"]
