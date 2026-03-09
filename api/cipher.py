"""
cipher.py - Main cipher interface combining encoding and encryption

This module provides the high-level CatCipher class that combines
cat sound encoding with optional password-based encryption.
"""

from .encoder import CatEncoder
from .crypto import PasswordCrypto


class CatCipher:
    """
    Main cipher class for encrypting/decrypting messages into cat sounds.

    This class combines the cat sound encoder with optional password-based
    encryption to provide a complete encryption solution.
    """

    def __init__(self):
        """Initialize the cat cipher with encoder and crypto modules"""
        self.encoder = CatEncoder()
        self.crypto = PasswordCrypto()

    def encrypt(self, message, password=None):
        """
        Encrypt a message into cat sounds.

        The encryption process:
        1. Convert message to bytes (if string)
        2. Apply password-based XOR encryption (if password provided)
        3. Encode encrypted bytes as cat sound words
        4. Join words with spaces

        Args:
            message: String or bytes to encrypt
            password: Optional password for encryption

        Returns:
            String of space-separated cat words
        """
        # Convert to bytes if string
        if isinstance(message, str):
            data = message.encode('utf-8')
        else:
            data = message

        # Apply password encryption if provided
        if password:
            data = self.crypto.encrypt(data, password)

        # Encode as cat sounds
        words = self.encoder.encode_bytes(data)
        return ' '.join(words)

    def decrypt(self, cat_text, password=None):
        """
        Decrypt cat sounds back into the original message.

        The decryption process:
        1. Split cat text into individual words
        2. Decode words back to bytes
        3. Apply password-based XOR decryption (if password provided)
        4. Return decrypted bytes

        Args:
            cat_text: String of space-separated cat words
            password: Optional password for decryption (must match encryption password)

        Returns:
            Bytes object with decrypted data

        Raises:
            ValueError: If cat words cannot be decoded
        """
        # Split into words and decode
        words = cat_text.strip().split()
        data = self.encoder.decode_words(words)

        # Apply password decryption if provided
        if password:
            data = self.crypto.decrypt(data, password)

        return data

    def encrypt_text(self, text, password=None):
        """
        Encrypt text and return cat sounds string.

        Args:
            text: String to encrypt
            password: Optional password

        Returns:
            String of cat sounds
        """
        return self.encrypt(text, password)

    def decrypt_text(self, cat_text, password=None):
        """
        Decrypt cat sounds and return text string.

        Args:
            cat_text: String of cat sounds
            password: Optional password

        Returns:
            Decrypted string

        Raises:
            ValueError: If decoding fails
            UnicodeDecodeError: If result is not valid UTF-8
        """
        data = self.decrypt(cat_text, password)
        return data.decode('utf-8')

    def encrypt_file(self, input_path, output_path, password=None):
        """
        Encrypt a file and save as cat sounds.

        Args:
            input_path: Path to input file
            output_path: Path to output file
            password: Optional password

        Raises:
            IOError: If file operations fail
        """
        with open(input_path, 'rb') as f:
            data = f.read()

        encrypted = self.encrypt(data, password)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(encrypted)

    def decrypt_file(self, input_path, output_path, password=None):
        """
        Decrypt a cat sounds file and save the result.

        Args:
            input_path: Path to cat sounds file
            output_path: Path to output file
            password: Optional password

        Raises:
            IOError: If file operations fail
            ValueError: If decoding fails
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            cat_text = f.read()

        decrypted = self.decrypt(cat_text, password)

        with open(output_path, 'wb') as f:
            f.write(decrypted)
