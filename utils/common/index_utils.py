# utils/common/index_utils.py

import os
from configs.config import SAVE_DIR, HUMAN_CREATED_DIR

def get_next_idx():
    """
    Returns the next available numeric index across saved_images/ and human_created/.
    """
    indices = []
    for folder in [SAVE_DIR, HUMAN_CREATED_DIR]:
        for f in os.listdir(folder):
            name, ext = os.path.splitext(f)
            if ext.lower() in (".png", ".jpg", ".jpeg") and name.isdigit():
                indices.append(int(name))
    return max(indices, default=-1) + 1
    