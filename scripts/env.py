import secrets
import string

SECRET_KEY_LENGTH = 50
DOMAIN = "2975645s.eu.pythonanywhere.com"

# generate a secure SECRET_KEY
chars = string.ascii_letters + string.digits + string.punctuation.replace('"', "")
secret_key = "".join(secrets.choice(chars) for _ in range(SECRET_KEY_LENGTH))

# write the .env file
contents = f'''SECRET_KEY="{secret_key}"
DOMAIN="{DOMAIN}"
'''

with open("../.env", "w") as f:
    f.write(contents)
