from pathlib import Path


def helper() -> str:
    return "helper"


def get_path() -> str:
    return str(Path(__file__).parent)
