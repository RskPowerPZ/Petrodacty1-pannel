# app/globals.py
import json
import os
from datetime import datetime, timedelta, timezone
from github_utils import read_file_from_github, write_file_to_github, append_to_logs


# --- Reset Date Helper (IST cutoff 4 AM) ---
def get_reset_date() -> str:
    """
    Return current reset date string (YYYY-MM-DD) in IST timezone.
    Cutoff: 4 AM IST → if before 4, considered as previous day.
    """
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    if now.hour >= 4:
        return now.date().isoformat()
    else:
        return (now - timedelta(days=1)).date().isoformat()


# --- JSON Load/Save Helpers ---
def load_json(filename: str) -> dict:
    """
    Try to load JSON from GitHub first, then fallback to local file.
    Returns {} if file not found or invalid.
    """
    try:
        # Try GitHub
        content = read_file_from_github(f"data/{filename}")
        if content:
            return json.loads(content)
    except Exception as e:
        print(f"[WARN] Error loading {filename} from GitHub: {e}")

    # Local fallback
    try:
        if os.path.exists(f"data/{filename}"):
            with open(f"data/{filename}", "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[WARN] Error loading {filename} locally: {e}")

    return {}


def save_json(filename: str, data: dict) -> None:
    """
    Save JSON to local file + push to GitHub.
    """
    try:
        os.makedirs("data", exist_ok=True)  # ensure data/ exists
        with open(f"data/{filename}", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Could not save {filename} locally: {e}")

    try:
        write_file_to_github(f"data/{filename}", json.dumps(data, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"[WARN] Could not write {filename} to GitHub: {e}")


# --- Globals (default safe empty dicts) ---
users: dict = {}
grants: dict = {}
vips: dict = {}
blocks: dict = {}
autos: dict = {}
bot = None  # Will be set later at runtime by main app