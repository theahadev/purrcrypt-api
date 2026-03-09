"""
crypto.py - Password-based encryption and key derivation

This module handles password-based encryption using SHA-256 for key derivation
and XOR cipher for data encryption.
"""

import hashlib


class PasswordCrypto:
    """Handles password-based encryption and decryption"""

    def __init__(self):
        """Initialize the crypto module"""
        pass

    def derive_key(self, password, length):
        """
        Derive a key from a password using SHA-256.

        This creates a deterministic key stream from a password by:
        1. Hashing the password with SHA-256 to get a seed
        2. Expanding the seed by repeatedly hashing (seed + counter)
        3. Returning the first 'length' bytes

        Args:
            password: String password
            length: Required key length in bytes

        Returns:
            Bytes object of the specified length
        """
        if not password:
            return bytes([0] * length)

        # Use SHA-256 to derive a key seed from the password
        key_seed = hashlib.sha256(password.encode('utf-8')).digest()

        # Expand the key to the required length
        key_stream = bytearray()
        counter = 0

        while len(key_stream) < length:
            # Hash (seed + counter) to generate more key material
            expanded = hashlib.sha256(
                key_seed + counter.to_bytes(4, 'big')
            ).digest()
            key_stream.extend(expanded)
            counter += 1

        return bytes(key_stream[:length])

    def xor_data(self, data, key):
        """
        XOR data with a key stream.

        Args:
            data: Bytes to encrypt/decrypt
            key: Key bytes to XOR with

        Returns:
            XOR'd bytes
        """
        if not key or len(key) == 0:
            return data

        result = bytearray()
        for i, byte in enumerate(data):
            result.append(byte ^ key[i % len(key)])

        return bytes(result)

    def encrypt(self, data, password):
        """
        Encrypt data using password-based XOR cipher.

        Args:
            data: Bytes to encrypt
            password: Password string (or None for no encryption)

        Returns:
            Encrypted bytes
        """
        if not password:
            return data

        key = self.derive_key(password, len(data))
        return self.xor_data(data, key)

    def decrypt(self, data, password):
        """
        Decrypt data using password-based XOR cipher.

        Note: XOR is symmetric, so encryption and decryption are the same operation.

        Args:
            data: Bytes to decrypt
            password: Password string (or None for no decryption)

        Returns:
            Decrypted bytes
        """
        # XOR is symmetric - encryption and decryption are the same
        return self.encrypt(data, password)


def encrypt_data(data, password=None):
    """
    Convenience function to encrypt data with a password.

    Args:
        data: Bytes or string to encrypt
        password: Optional password string

    Returns:
        Encrypted bytes
    """
    if isinstance(data, str):
        data = data.encode('utf-8')

    crypto = PasswordCrypto()
    return crypto.encrypt(data, password)


def decrypt_data(data, password=None):
    """
    Convenience function to decrypt data with a password.

    Args:
        data: Bytes to decrypt
        password: Optional password string

    Returns:
        Decrypted bytes
    """
    crypto = PasswordCrypto()
    return crypto.decrypt(data, password)
