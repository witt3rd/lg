import os

import chromadb
from dotenv import load_dotenv

#

load_dotenv()
DB_DIR = os.getenv("DB_DIR", "./.db")

#


class ToolRegistry:
    def __init__(self) -> None:
        print(f"DB_DIR: {DB_DIR}")
        os.makedirs(DB_DIR, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=DB_DIR)
        self.collection = self.chroma_client.get_or_create_collection("tool_registry")
