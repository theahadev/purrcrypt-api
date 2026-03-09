#!/usr/bin/env python3
"""
main.py - Command-line interface for PurrCrypt Python

This module provides the CLI for encrypting and decrypting messages
into adorable cat sounds.
"""

import sys
import argparse
import getpass
from pathlib import Path

from .cipher import CatCipher


class PurrCryptCLI:
    """Command-line interface for PurrCrypt"""

    def __init__(self):
        """Initialize the CLI"""
        self.cipher = CatCipher()

    def get_password(self, password_arg):
        """
        Get password from argument or prompt user.

        Args:
            password_arg: Password from command line (None, '', or actual password)

        Returns:
            Password string or None
        """
        if password_arg is None:
            return None
        elif password_arg == '':
            # Prompt for password securely
            return getpass.getpass('🔐 Enter password: ')
        else:
            return password_arg

    def validate_text(self, data, password_used):
        """
        Validate if decrypted data looks like valid text.

        Args:
            data: Bytes to validate
            password_used: Whether a password was used

        Returns:
            Tuple of (is_valid, message)
        """
        try:
            text = data.decode('utf-8')

            # Basic heuristic: check if mostly printable ASCII or valid Unicode
            printable_ratio = sum(1 for c in text if c.isprintable() or c in '\n\r\t') / len(text) if text else 0

            if printable_ratio < 0.7 and password_used:
                return False, "Invalid password or corrupted data"

            return True, text
        except UnicodeDecodeError:
            if password_used:
                return False, "Invalid password or corrupted data"
            else:
                return False, "Corrupted data or invalid encoding"

    def encrypt_command(self, args):
        """
        Handle encrypt command.

        Args:
            args: Parsed command-line arguments

        Returns:
            Exit code (0 for success)
        """
        # Get password if specified
        password = self.get_password(args.password)

        # Get input
        if args.input:
            try:
                with open(args.input, 'rb') as f:
                    data = f.read()
                message = data.decode('utf-8', errors='replace')
            except IOError as e:
                print(f"❌ Error reading input file: {e}", file=sys.stderr)
                return 1
        elif args.message:
            message = args.message
        else:
            print("❌ Error: Provide a message or input file", file=sys.stderr)
            print("Usage: purrcrypt encrypt 'your message' or -i input.txt", file=sys.stderr)
            return 1

        # Encrypt
        try:
            encrypted = self.cipher.encrypt(message, password=password)
        except Exception as e:
            print(f"❌ Error during encryption: {e}", file=sys.stderr)
            return 1

        # Output
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(encrypted)
                if password:
                    print(f"🔒 Encrypted with password to {args.output}")
                else:
                    print(f"✓ Encrypted to {args.output}")
            except IOError as e:
                print(f"❌ Error writing output file: {e}", file=sys.stderr)
                return 1
        else:
            print("Encrypted message:")
            print(encrypted)

        return 0

    def decrypt_command(self, args):
        """
        Handle decrypt command.

        Args:
            args: Parsed command-line arguments

        Returns:
            Exit code (0 for success)
        """
        # Get password if specified
        password = self.get_password(args.password)

        # Get input
        if args.input:
            try:
                with open(args.input, 'r', encoding='utf-8') as f:
                    cat_text = f.read()
            except IOError as e:
                print(f"❌ Error reading input file: {e}", file=sys.stderr)
                return 1
        elif args.message:
            cat_text = args.message
        else:
            print("❌ Error: Provide cat sounds or input file", file=sys.stderr)
            print("Usage: purrcrypt decrypt 'meow purr nya' or -i encrypted.meow", file=sys.stderr)
            return 1

        # Decrypt
        try:
            decrypted = self.cipher.decrypt(cat_text, password=password)
        except ValueError as e:
            print(f"❌ Error decrypting: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"❌ Unexpected error during decryption: {e}", file=sys.stderr)
            return 1

        # Validate and decode
        is_valid, result = self.validate_text(decrypted, password is not None)

        if not is_valid:
            print(f"❌ Decryption failed: {result}", file=sys.stderr)
            return 1

        message = result

        # Warn if suspicious
        if password and any(ord(c) > 127 and c not in message[:100] for c in message[:min(100, len(message))]):
            print("⚠️  Warning: Decrypted text may be corrupted. Wrong password?", file=sys.stderr)

        # Output
        if args.output:
            try:
                with open(args.output, 'wb') as f:
                    f.write(decrypted)
                if password:
                    print(f"🔓 Decrypted with password to {args.output}")
                else:
                    print(f"✓ Decrypted to {args.output}")
            except IOError as e:
                print(f"❌ Error writing output file: {e}", file=sys.stderr)
                return 1
        else:
            print("Decrypted message:")
            print(message)

        return 0


def create_parser():
    """
    Create the argument parser for the CLI.

    Returns:
        ArgumentParser object
    """
    parser = argparse.ArgumentParser(
        prog='purrcrypt',
        description='🐱 PurrCrypt Python - Encrypt messages into cat sounds!',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encrypt a message
  %(prog)s encrypt "Hello, World!"

  # Encrypt with password (will prompt)
  %(prog)s encrypt "Secret message" -p

  # Encrypt with password (inline)
  %(prog)s encrypt "Secret message" -p mypassword

  # Decrypt cat sounds
  %(prog)s decrypt "meww purrr nnya meow"

  # Encrypt from file with password
  %(prog)s encrypt -i input.txt -o encrypted.meow -p

  # Decrypt from file
  %(prog)s decrypt -i encrypted.meow -o decrypted.txt -p

For more information, visit: https://github.com/yourusername/purrcrypt
        """
    )

    # Add version
    parser.add_argument(
        '--version',
        action='version',
        version='PurrCrypt Python 1.3.0'
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Command to execute',
        required=False
    )

    # Encrypt command
    encrypt_parser = subparsers.add_parser(
        'encrypt',
        help='Encrypt a message into cat sounds',
        description='Encrypt text or files into adorable cat sounds'
    )
    encrypt_parser.add_argument(
        'message',
        nargs='?',
        help='Message to encrypt (use quotes for spaces)'
    )
    encrypt_parser.add_argument(
        '-i', '--input',
        metavar='FILE',
        help='Input file to encrypt'
    )
    encrypt_parser.add_argument(
        '-o', '--output',
        metavar='FILE',
        help='Output file for encrypted message'
    )
    encrypt_parser.add_argument(
        '-p', '--password',
        nargs='?',
        const='',
        metavar='PASSWORD',
        help='Password for encryption (omit value to prompt securely)'
    )

    # Decrypt command
    decrypt_parser = subparsers.add_parser(
        'decrypt',
        help='Decrypt cat sounds back to message',
        description='Decrypt cat sounds back to the original text'
    )
    decrypt_parser.add_argument(
        'message',
        nargs='?',
        help='Cat sounds to decrypt (use quotes)'
    )
    decrypt_parser.add_argument(
        '-i', '--input',
        metavar='FILE',
        help='Input file with cat sounds'
    )
    decrypt_parser.add_argument(
        '-o', '--output',
        metavar='FILE',
        help='Output file for decrypted message'
    )
    decrypt_parser.add_argument(
        '-p', '--password',
        nargs='?',
        const='',
        metavar='PASSWORD',
        help='Password for decryption (omit value to prompt securely)'
    )

    return parser


def main():
    """Main entry point for the CLI"""
    parser = create_parser()
    args = parser.parse_args()

    # Show help if no command specified
    if not args.command:
        parser.print_help()
        return 0

    # Create CLI instance
    cli = PurrCryptCLI()

    # Route to appropriate command
    if args.command == 'encrypt':
        return cli.encrypt_command(args)
    elif args.command == 'decrypt':
        return cli.decrypt_command(args)
    else:
        print(f"❌ Unknown command: {args.command}", file=sys.stderr)
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
