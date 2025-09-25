# github_utils.py
from github import Github
from config import GITHUB_TOKEN, GITHUB_REPO


def get_github_client() -> Github:
    """Return a GitHub client using the configured token."""
    return Github(GITHUB_TOKEN)


def read_file_from_github(path: str) -> str | None:
    """
    Read a file from the configured GitHub repo.
    Returns the decoded string content, or None if not found/error.
    """
    try:
        g = get_github_client()
        repo = g.get_repo(GITHUB_REPO)
        file_content = repo.get_contents(path)
        return file_content.decoded_content.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[WARN] Could not read {path} from GitHub: {e}")
        return None


def write_file_to_github(path: str, content: str) -> bool:
    """
    Write (create or update) a file in the configured GitHub repo.
    Returns True on success, False on failure.
    """
    try:
        g = get_github_client()
        repo = g.get_repo(GITHUB_REPO)

        # Try update if file exists
        try:
            file = repo.get_contents(path)
            repo.update_file(
                path,
                f"Update {path}",
                content,
                file.sha,
                branch="main",  # ensure writing to main branch
            )
            return True
        except Exception:
            # File doesn't exist -> create
            repo.create_file(
                path,
                f"Create {path}",
                content,
                branch="main",
            )
            return True

    except Exception as e:
        print(f"[ERROR] GitHub write error for {path}: {e}")
        return False


def append_to_logs(content: str) -> bool:
    """
    Append a line to data/logs.txt in the repo.
    Ensures file is created if missing.
    Returns True on success, False on failure.
    """
    try:
        g = get_github_client()
        repo = g.get_repo(GITHUB_REPO)
        path = "data/logs.txt"

        try:
            file = repo.get_contents(path)
            old = file.decoded_content.decode("utf-8", errors="ignore")
            new_content = old.rstrip("\n") + "\n" + content + "\n"
            repo.update_file(
                path,
                "Append to logs.txt",
                new_content,
                file.sha,
                branch="main",
            )
            return True
        except Exception:
            # logs.txt does not exist -> create new
            repo.create_file(
                path,
                "Create logs.txt",
                content + "\n",
                branch="main",
            )
            return True

    except Exception as e:
        print(f"[ERROR] GitHub log append error: {e}")
        return False