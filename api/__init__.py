"""
PurrCrypt Python - Encrypt messages into adorable cat sounds!

A simple and fun encryption tool that converts text into meows, purrs, and other cat sounds.
"""

from .cipher import CatCipher
from .encoder import CatEncoder
from .crypto import encrypt_data, decrypt_data

__version__ = '1.4.0'
__all__ = ['CatCipher', 'CatEncoder', 'encrypt_data', 'decrypt_data']
