#!/usr/bin/env python3
"""
PurrCrypt Python - Entry point script

This script serves as the main entry point for the PurrCrypt Python CLI.
It imports and runs the main module from the purrcrypt_py package.

Usage:
    python3 purrcrypt.py encrypt "Hello, World!"
    python3 purrcrypt.py decrypt "meow purr nya"
"""

import sys
from pathlib import Path

# Add the parent directory to the path to allow imports
sys.path.insert(0, str(Path(__file__).parent))

from purrcrypt_py.main import main

if __name__ == '__main__':
    sys.exit(main())
