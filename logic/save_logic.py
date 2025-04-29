# logic/save_logic.py

import shutil
import os
import streamlit as st
from utils.common.human_upload import save_human_record
from configs.config import TMP_UPLOAD_DIR

def save_single_record(record):
    """
    Save a single human record (good one) to Drive.
    """
    save_human_record(record)

def handle_save_batch():
    """
    Old batch saving not needed anymore.
    """
    pass  # Not used anymore
