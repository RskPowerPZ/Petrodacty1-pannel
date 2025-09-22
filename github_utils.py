# github_utils.py
from github import Github
from config import GITHUB_TOKEN, GITHUB_REPO
import os

def get_github_client():
    return Github(GITHUB_TOKEN)

def read_file_from_github(path):
    try:
        g = get_github_client()
        repo = g.get_repo(GITHUB_REPO)
        file_content = repo.get_contents(path)
        return file_content.decoded_content.decode()
    except Exception:
        return None

def write_file_to_github(path, content):
    try:
        g = get_github_client()
        repo = g.get_repo(GITHUB_REPO)
        try:
            file = repo.get_contents(path)
            repo.update_file(path, f"Update {path}", content, file.sha)
        except:
            repo.create_file(path, f"Create {path}", content)
    except Exception as e:
        print(f"GitHub write error: {e}")

def append_to_logs(content):
    try:
        g = get_github_client()
        repo = g.get_repo(GITHUB_REPO)
        path = 'data/logs.txt'
        try:
            file = repo.get_contents(path)
            updated_content = file.decoded_content.decode() + content + '\n'
            repo.update_file(path, "Append to logs", updated_content, file.sha)
        except:
            repo.create_file(path, "Create logs.txt", content + '\n')
    except Exception as e:
        print(f"GitHub log append error: {e}")