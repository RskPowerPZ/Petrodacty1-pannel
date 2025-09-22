# app/globals.py
import json
import os
from datetime import datetime, timedelta, timezone
from github_utils import read_file_from_github, write_file_to_github

def get_reset_date():
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    if now.hour >= 4:
        return now.date().isoformat()
    else:
        return (now - timedelta(days=1)).date().isoformat()

def load_json(filename):
    try:
        content = read_file_from_github(f'data/{filename}')
        if content:
            return json.loads(content)
        return {}
    except Exception as e:
        print(f"Error loading {filename} from GitHub: {e}")
        return {}

def save_json(filename, data):
    try:
        with open(f'data/{filename}', 'w') as f:
            json.dump(data, f, indent=4)
        write_file_to_github(f'data/{filename}', json.dumps(data, indent=4))
    except Exception as e:
        print(f"Error saving {filename} to GitHub: {e}")

users = None
grants = None
vips = None
blocks = None
autos = None
bot = None