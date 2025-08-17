#!/usr/bin/env python3
"""
Generate a secure Django secret key.
Usage: python generate_secret_key.py
"""

import secrets
import string


def generate_secret_key(length=50):
    """Generate a secure random secret key."""
    # Use a mix of letters, digits, and special characters
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # Remove characters that might cause issues in environment files
    alphabet = alphabet.replace('"', '').replace("'", '').replace('\\', '')
    
    # Generate the secret key
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secret_key


def main():
    """Generate and display a secure secret key."""
    print("🔐 Generating secure Django secret key...")
    print("=" * 50)
    
    # Generate multiple keys for different environments
    development_key = generate_secret_key(50)
    production_key = generate_secret_key(100)
    
    print("Development Secret Key (50 chars):")
    print(f"SECRET_KEY={development_key}")
    print()
    
    print("Production Secret Key (100 chars):")
    print(f"SECRET_KEY={production_key}")
    print()
    
    print("📝 Instructions:")
    print("1. Copy one of the keys above")
    print("2. Add it to your .env file:")
    print("   SECRET_KEY=your_generated_key_here")
    print("3. Or set it as an environment variable")
    print()
    
    print("⚠️  Security Notes:")
    print("- Never commit your secret key to version control")
    print("- Use different keys for development and production")
    print("- Keep your production key secure and private")
    print("- Rotate keys periodically in production")


if __name__ == "__main__":
    main()
