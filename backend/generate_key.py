import secrets
import os

def generate_secret_key(length=32):
    """Generates a secure random secret key."""
    return secrets.token_hex(length)

def update_flask_settings(filepath=".env"):
    """Updates the SECRET_KEY in a Flask settings file (e.g., .env)."""
    new_secret_key = generate_secret_key()
    updated_lines = []
    key_found = False

    try:
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith("SECRET_KEY="):
                    updated_lines.append(f"SECRET_KEY={new_secret_key}\n")
                    key_found = True
                else:
                    updated_lines.append(line)

        with open(filepath, 'w') as f:
            f.writelines(updated_lines)

        if not key_found:
            with open(filepath, 'a') as f:
                f.write(f"SECRET_KEY={new_secret_key}\n")
            print(f"SECRET_KEY added to {filepath}")
        else:
            print(f"SECRET_KEY updated in {filepath}")

        print(f"Generated Secret Key: {new_secret_key}")

    except FileNotFoundError:
        with open(filepath, 'w') as f:
            f.write(f"SECRET_KEY={new_secret_key}\n")
            f.write("DEBUG=True\n")
            f.write("HOST=0.0.0.0\n")
            f.write("PORT=5000\n")
        print(f"{filepath} created with a new SECRET_KEY and default settings.")
        print(f"Generated Secret Key: {new_secret_key}")

if __name__ == "__main__":
    update_flask_settings()
