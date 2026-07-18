import os
from typing import List

def read_file(filepath: str) -> str:
    """Reads and returns the content of a file.

    Args:
        filepath: The absolute or relative path to the file to read.

    Returns:
        The content of the file as a string.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath: str, content: str) -> str:
    """Writes content to a file. Overwrites the file if it exists.

    Args:
        filepath: The absolute or relative path to the file to write to.
        content: The text content to write into the file.

    Returns:
        A success message indicating the file was written.
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"Successfully wrote to {filepath}"

def list_directory(path: str) -> List[str]:
    """Returns a list of files and directories in the specified path.

    Args:
        path: The path of the directory to list.

    Returns:
        A list of names of files and directories.
    """
    return os.listdir(path)
