import re
from typing import Optional
from config import PROFILE_PHOTOS_DIR, ID_PHOTOS_DIR
import uuid
import os

def validate_course(text: str) -> Optional[int]:
    # Accept '1', '1-ый', '1-й', '1 курс', '1-ый курс'
    m = re.search(r"([1-4])", text)
    if m:
        return int(m.group(1))
    return None

def validate_age(text: str) -> Optional[int]:
    if not text.isdigit():
        return None
    val = int(text)
    if val < 16 or val > 100:
        return None
    return val

def validate_name(text: str) -> Optional[str]:
    text = text.strip()
    if 1 <= len(text) <= 60:
        # slight sanitization
        if re.search(r"[^0-9A-Za-zА-Яа-яЁё \-']", text):
            return None
        return text
    return None

def validate_description(text: str) -> Optional[str]:
    text = text.strip()
    if 0 < len(text) <= 300:
        return text
    return None

def save_profile_photo(file_bytes: bytes, file_name: str = None) -> str:
    if not file_name:
        file_name = f"{uuid.uuid4().hex}.jpg"
    path = PROFILE_PHOTOS_DIR / file_name
    with open(path, "wb") as f:
        f.write(file_bytes)
    return str(path)

def save_id_photo(file_bytes: bytes, file_name: str = None) -> str:
    if not file_name:
        file_name = f"{uuid.uuid4().hex}.jpg"
    path = ID_PHOTOS_DIR / file_name
    with open(path, "wb") as f:
        f.write(file_bytes)
    return str(path)

def remove_file(path: str):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception as e:
        # log if desired
        print("Failed to remove file", path, e)
