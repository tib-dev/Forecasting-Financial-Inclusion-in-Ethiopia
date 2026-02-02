from pathlib import Path


def get_project_root() -> Path:
    """
    Return the project root by climbing upward until a folder
    containing known project markers is found.

    This is safer than hardcoding parent levels and works even
    if the file structure changes.
    """
    current = Path(__file__).resolve()

    markers = {"config", "src", "requirements.txt", "pyproject.toml"}

    for parent in current.parents:
        if any((parent / m).exists() for m in markers):
            return parent

    raise RuntimeError(
        "Could not determine project root. No known project markers found."
    )
