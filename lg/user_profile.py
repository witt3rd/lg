"""Bionic bot"""

import os

from dotenv import load_dotenv

#

load_dotenv()
DB_DIR = os.getenv("DB_DIR", "./.db")
PROFILES_DIR = os.path.join(DB_DIR, "profiles")

#


def load_user_profile(user_name: str) -> str | None:
    path = os.path.join(PROFILES_DIR, f"{user_name}.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


def save_user_profile(user_name: str, user_profile: str) -> None:
    path = os.path.join(PROFILES_DIR, f"{user_name}.txt")
    os.makedirs(PROFILES_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(user_profile)
