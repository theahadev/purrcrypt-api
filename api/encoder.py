"""
encoder.py - Cat sound pattern encoding and decoding

This module handles the conversion between bits and cat sound words.
Each cat sound pattern encodes 6 bits through character repetitions.
"""


class CatPattern:
    """Represents a single cat sound pattern (mew, purr, nya, etc.)"""

    def __init__(self, name, chars):
        """
        Initialize a cat pattern.

        Args:
            name: Name of the pattern (e.g., 'mew', 'purr')
            chars: List of characters that make up the pattern
        """
        self.name = name
        self.chars = chars
        self.is_special = len(chars) == 4  # Special patterns like 'meow'

    def encode(self, bits):
        """
        Encode 6 bits into a cat word using this pattern.

        Args:
            bits: Integer value 0-63 (6 bits)

        Returns:
            String representation of the cat word
        """
        bits = bits & 0x3F  # Ensure only 6 bits

        if self.is_special:
            # Special 4-character pattern (e.g., 'meow')
            # Split 6 bits: 2 bits per first two chars, 1 bit per last two chars
            count1 = ((bits >> 4) & 0x03) + 1  # Bits 5-4: 1-4 repetitions
            count2 = ((bits >> 2) & 0x03) + 1  # Bits 3-2: 1-4 repetitions
            count3 = ((bits >> 1) & 0x01) + 1  # Bit 1: 1-2 repetitions
            count4 = (bits & 0x01) + 1         # Bit 0: 1-2 repetitions

            return (self.chars[0] * count1 +
                    self.chars[1] * count2 +
                    self.chars[2] * count3 +
                    self.chars[3] * count4)
        else:
            # Complex 3-character pattern (e.g., 'mew', 'purr')
            # Split 6 bits: 2 bits per character (1-4 repetitions each)
            count1 = ((bits >> 4) & 0x03) + 1  # Bits 5-4
            count2 = ((bits >> 2) & 0x03) + 1  # Bits 3-2
            count3 = (bits & 0x03) + 1         # Bits 1-0

            return (self.chars[0] * count1 +
                    self.chars[1] * count2 +
                    self.chars[2] * count3)

    def decode(self, word):
        """
        Decode a cat word back into 6 bits.

        Args:
            word: String cat word to decode

        Returns:
            Integer value 0-63, or None if word doesn't match pattern
        """
        word = word.lower().strip()
        if not word:
            return None

        # Check if word contains only this pattern's characters
        if not all(c in self.chars for c in word if c.isalpha()):
            return None

        # Count each character
        counts = [word.count(c) for c in self.chars]

        # Validate counts
        if self.is_special:
            # First two: 1-4, last two: 1-2
            if counts[0] < 1 or counts[0] > 4 or counts[1] < 1 or counts[1] > 4:
                return None
            if counts[2] < 1 or counts[2] > 2 or counts[3] < 1 or counts[3] > 2:
                return None

            # Decode 4-character pattern
            bits1 = (counts[0] - 1) & 0x03
            bits2 = (counts[1] - 1) & 0x03
            bits3 = (counts[2] - 1) & 0x01
            bits4 = (counts[3] - 1) & 0x01

            return (bits1 << 4) | (bits2 << 2) | (bits3 << 1) | bits4
        else:
            # All characters: 1-4 repetitions
            if any(c < 1 or c > 4 for c in counts):
                return None

            # Decode 3-character pattern
            bits1 = (counts[0] - 1) & 0x03
            bits2 = (counts[1] - 1) & 0x03
            bits3 = (counts[2] - 1) & 0x03

            return (bits1 << 4) | (bits2 << 2) | bits3

    def matches(self, word):
        """
        Check if a word matches this pattern.

        Args:
            word: String to check

        Returns:
            Boolean indicating if word matches this pattern
        """
        word = word.lower().strip()
        return all(c in self.chars for c in word if c.isalpha())


class CatEncoder:
    """Handles encoding and decoding between bytes and cat sounds"""

    # Define all cat sound patterns
    PATTERNS = [
        CatPattern('mew', ['m', 'e', 'w']),
        CatPattern('purr', ['p', 'u', 'r']),
        CatPattern('nya', ['n', 'y', 'a']),
        CatPattern('meow', ['m', 'e', 'o', 'w']),
        CatPattern('mrrp', ['m', 'r', 'p']),
    ]

    def __init__(self):
        """Initialize the cat encoder"""
        pass

    def encode_word(self, bits, pattern_index):
        """
        Encode bits into a cat word using the specified pattern.

        Args:
            bits: Integer value to encode (6 bits or less)
            pattern_index: Index of the pattern to use

        Returns:
            String cat word
        """
        pattern = self.PATTERNS[pattern_index % len(self.PATTERNS)]
        return pattern.encode(bits)

    def decode_word(self, word):
        """
        Decode a cat word back into bits.

        Args:
            word: String cat word to decode

        Returns:
            Tuple of (pattern_index, bits_value) or None if invalid
        """
        word = word.lower().strip()
        if not word:
            return None

        # Try each pattern
        for idx, pattern in enumerate(self.PATTERNS):
            if pattern.matches(word):
                bits = pattern.decode(word)
                if bits is not None:
                    return (idx, bits)

        return None

    def encode_bytes(self, data):
        """
        Encode bytes into a list of cat words.

        Args:
            data: Bytes to encode

        Returns:
            List of cat word strings
        """
        words = []
        i = 0

        while i < len(data):
            remaining = len(data) - i

            if remaining >= 3:
                # Process 3 bytes (24 bits) -> 4 words (6 bits each)
                byte1, byte2, byte3 = data[i], data[i + 1], data[i + 2]
                packed = (byte1 << 16) | (byte2 << 8) | byte3

                # Extract 4 groups of 6 bits
                words.append(self.encode_word((packed >> 18) & 0x3F, 0))
                words.append(self.encode_word((packed >> 12) & 0x3F, 1))
                words.append(self.encode_word((packed >> 6) & 0x3F, 2))
                words.append(self.encode_word(packed & 0x3F, 3))

                i += 3
            elif remaining == 2:
                # Process 2 bytes (16 bits) -> 3 words
                byte1, byte2 = data[i], data[i + 1]
                packed = (byte1 << 8) | byte2

                # Split into 5, 6, 5 bits
                words.append(self.encode_word((packed >> 11) & 0x1F, 0))
                words.append(self.encode_word((packed >> 5) & 0x3F, 1))
                words.append(self.encode_word(packed & 0x1F, 2))

                i += 2
            else:
                # Process 1 byte (8 bits) -> 2 words (4 bits each)
                byte = data[i]
                words.append(self.encode_word((byte >> 4) & 0x0F, 0))
                words.append(self.encode_word(byte & 0x0F, 1))

                i += 1

        return words

    def decode_words(self, words):
        """
        Decode cat words back into bytes.

        Args:
            words: List of cat word strings

        Returns:
            Bytearray of decoded data

        Raises:
            ValueError: If words cannot be decoded
        """
        result = bytearray()
        i = 0

        while i < len(words):
            remaining = len(words) - i

            if remaining >= 4:
                # Decode 4 words -> 3 bytes (24 bits)
                decoded = [self.decode_word(words[i + j]) for j in range(4)]

                if any(d is None for d in decoded):
                    raise ValueError(f"Failed to decode words at position {i}")

                bits1 = decoded[0][1] & 0x3F
                bits2 = decoded[1][1] & 0x3F
                bits3 = decoded[2][1] & 0x3F
                bits4 = decoded[3][1] & 0x3F

                value = (bits1 << 18) | (bits2 << 12) | (bits3 << 6) | bits4

                result.append((value >> 16) & 0xFF)
                result.append((value >> 8) & 0xFF)
                result.append(value & 0xFF)

                i += 4
            elif remaining >= 3:
                # Decode 3 words -> 2 bytes (16 bits)
                decoded = [self.decode_word(words[i + j]) for j in range(3)]

                if any(d is None for d in decoded):
                    raise ValueError(f"Failed to decode words at position {i}")

                bits1 = decoded[0][1] & 0x1F
                bits2 = decoded[1][1] & 0x3F
                bits3 = decoded[2][1] & 0x1F

                value = (bits1 << 11) | (bits2 << 5) | bits3

                result.append((value >> 8) & 0xFF)
                result.append(value & 0xFF)

                i += 3
            elif remaining >= 2:
                # Decode 2 words -> 1 byte (8 bits)
                decoded = [self.decode_word(words[i + j]) for j in range(2)]

                if any(d is None for d in decoded):
                    raise ValueError(f"Failed to decode words at position {i}")

                high = decoded[0][1] & 0x0F
                low = decoded[1][1] & 0x0F

                result.append((high << 4) | low)

                i += 2
            else:
                break

        return bytes(result)

    def encode_string(self, text):
        """
        Encode a text string into cat sounds.

        Args:
            text: String to encode

        Returns:
            String of space-separated cat words
        """
        data = text.encode('utf-8')
        words = self.encode_bytes(data)
        return ' '.join(words)

    def decode_string(self, cat_text):
        """
        Decode cat sounds back into text.

        Args:
            cat_text: String of space-separated cat words

        Returns:
            Decoded string

        Raises:
            ValueError: If decoding fails
        """
        words = cat_text.strip().split()
        data = self.decode_words(words)
        return data.decode('utf-8')
