import os

from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault(
    "LANGFUSE_HOST",
    os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)

from langfuse import get_client

langfuse = get_client()

langfuse.auth_check()