import secrets
import string
from pathlib import Path

ROOT_DIR = BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY_LENGTH = 50
DOMAIN = "2975645s.eu.pythonanywhere.com"

if __name__ == "__main__":
    # generate a secure SECRET_KEY
    chars = string.ascii_letters + string.digits + string.punctuation.replace('"', "")
    secret_key = "".join(secrets.choice(chars) for _ in range(SECRET_KEY_LENGTH))

    # generate an easy to type password
    password_chars = string.ascii_letters + string.digits
    password = "".join(secrets.choice(password_chars) for _ in range(12))

    # write the .env file
    contents = f'''SECRET_KEY="{secret_key}"
DOMAIN="{DOMAIN}"
PASSWORD="{password}"'''

    with open(ROOT_DIR / ".env", "w") as f:
        f.write(contents)
