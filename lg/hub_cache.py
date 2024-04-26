import json
import os
from typing import Any

from dotenv import load_dotenv
from langchain import hub
from langchain_core.load import dumps, load

#

load_dotenv()
HUB_CACHE_DIR = os.getenv("HUB_CACHE_DIR", "./.hub_cache")

#


def safe_name(name: str) -> str:
    return name.replace("/", ".").lower()


def hub_pull(owner_repo_commit: str) -> Any:
    safe_owner_repo_commit = safe_name(owner_repo_commit)
    # check if it exists locally
    prompt_path = os.path.join(HUB_CACHE_DIR, f"{safe_owner_repo_commit}.json")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return load(json.loads(f.read()))
    # if not, pull from hub
    prompt = hub.pull(owner_repo_commit)
    # ensure directory exists
    os.makedirs(HUB_CACHE_DIR, exist_ok=True)
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(dumps(prompt))
    return prompt
