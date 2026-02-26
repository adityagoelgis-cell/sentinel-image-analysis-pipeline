import os


def ensure_dir(path: str):
    """
    Create directory if it does not exist.
    """
    os.makedirs(path, exist_ok=True)


def log(message: str):
    """
    Simple console logger.
    """
    print(f"[INFO] {message}")