"""
utils.py - Utility functions for PurrCrypt Python

This module provides helper functions for file operations,
validation, and other common tasks.
"""

import os
import sys
from pathlib import Path


def read_file_bytes(filepath):
    """
    Read a file and return its contents as bytes.

    Args:
        filepath: Path to the file

    Returns:
        Bytes object with file contents

    Raises:
        IOError: If file cannot be read
    """
    try:
        with open(filepath, 'rb') as f:
            return f.read()
    except IOError as e:
        raise IOError(f"Failed to read file '{filepath}': {e}")


def write_file_bytes(filepath, data):
    """
    Write bytes to a file.

    Args:
        filepath: Path to the file
        data: Bytes to write

    Raises:
        IOError: If file cannot be written
    """
    try:
        with open(filepath, 'wb') as f:
            f.write(data)
    except IOError as e:
        raise IOError(f"Failed to write file '{filepath}': {e}")


def read_file_text(filepath, encoding='utf-8'):
    """
    Read a file and return its contents as text.

    Args:
        filepath: Path to the file
        encoding: Text encoding (default: utf-8)

    Returns:
        String with file contents

    Raises:
        IOError: If file cannot be read
    """
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except IOError as e:
        raise IOError(f"Failed to read file '{filepath}': {e}")


def write_file_text(filepath, text, encoding='utf-8'):
    """
    Write text to a file.

    Args:
        filepath: Path to the file
        text: String to write
        encoding: Text encoding (default: utf-8)

    Raises:
        IOError: If file cannot be written
    """
    try:
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(text)
    except IOError as e:
        raise IOError(f"Failed to write file '{filepath}': {e}")


def is_valid_utf8(data):
    """
    Check if bytes represent valid UTF-8 text.

    Args:
        data: Bytes to check

    Returns:
        Boolean indicating if data is valid UTF-8
    """
    try:
        data.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False


def is_printable_text(text, threshold=0.7):
    """
    Check if text is mostly printable characters.

    Args:
        text: String to check
        threshold: Minimum ratio of printable characters (0.0-1.0)

    Returns:
        Boolean indicating if text is mostly printable
    """
    if not text:
        return True

    printable_count = sum(
        1 for c in text
        if c.isprintable() or c in '\n\r\t'
    )
    ratio = printable_count / len(text)

    return ratio >= threshold


def validate_decrypted_text(data, password_used=False):
    """
    Validate if decrypted data looks like valid text.

    Args:
        data: Bytes to validate
        password_used: Whether a password was used for decryption

    Returns:
        Tuple of (is_valid, error_message, decoded_text)
    """
    # Try to decode as UTF-8
    if not is_valid_utf8(data):
        if password_used:
            return (False, "Invalid password or corrupted data", None)
        else:
            return (False, "Corrupted data or invalid encoding", None)

    text = data.decode('utf-8')

    # Check if mostly printable
    if not is_printable_text(text, threshold=0.7) and password_used:
        return (False, "Invalid password or corrupted data", None)

    return (True, None, text)


def format_bytes_size(size_bytes):
    """
    Format byte size as human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 KB", "2.3 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def ensure_directory_exists(filepath):
    """
    Ensure the directory for a file path exists.

    Args:
        filepath: Path to a file

    Raises:
        OSError: If directory cannot be created
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create directory '{directory}': {e}")


def get_file_extension(filepath, default='.meow'):
    """
    Get or suggest file extension.

    Args:
        filepath: Path to check
        default: Default extension to return

    Returns:
        File extension string (including the dot)
    """
    ext = os.path.splitext(filepath)[1]
    return ext if ext else default


def is_cat_sounds_file(filepath):
    """
    Check if a file likely contains cat sounds based on content.

    Args:
        filepath: Path to the file

    Returns:
        Boolean indicating if file likely contains cat sounds
    """
    try:
        text = read_file_text(filepath)
        words = text.strip().split()

        if not words:
            return False

        # Check if words look like cat sounds
        cat_chars = set('mewpurnyaof')
        for word in words[:10]:  # Check first 10 words
            word_lower = word.lower()
            if not all(c in cat_chars for c in word_lower if c.isalpha()):
                return False

        return True
    except:
        return False


def count_words(text):
    """
    Count words in text.

    Args:
        text: String to count words in

    Returns:
        Integer word count
    """
    return len(text.split())


def estimate_encryption_size(input_size):
    """
    Estimate the size of encrypted output.

    Args:
        input_size: Size of input in bytes

    Returns:
        Estimated output size in bytes
    """
    # Each 3 bytes becomes 4 words
    # Average word length is about 6-8 characters
    # Add spaces between words
    words_count = (input_size // 3) * 4
    if input_size % 3 == 2:
        words_count += 3
    elif input_size % 3 == 1:
        words_count += 2

    avg_word_length = 7
    avg_space_length = 1

    return words_count * (avg_word_length + avg_space_length)


def print_error(message, file=sys.stderr):
    """
    Print an error message to stderr.

    Args:
        message: Error message to print
        file: File object to write to (default: stderr)
    """
    print(f"❌ {message}", file=file)


def print_success(message):
    """
    Print a success message to stdout.

    Args:
        message: Success message to print
    """
    print(f"✓ {message}")


def print_warning(message, file=sys.stderr):
    """
    Print a warning message to stderr.

    Args:
        message: Warning message to print
        file: File object to write to (default: stderr)
    """
    print(f"⚠️  {message}", file=file)


def print_info(message):
    """
    Print an info message to stdout.

    Args:
        message: Info message to print
    """
    print(f"ℹ️  {message}")
