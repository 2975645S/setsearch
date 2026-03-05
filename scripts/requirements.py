"""
Generate a requirements.txt file.
"""
import shutil
import subprocess

KWARGS = {
    "capture_output": True,
    "text": True,
    "check": True,
    "shell": True
}

if __name__ == "__main__":
    has_uv = shutil.which("uv") is not None

    if has_uv:
        contents = subprocess.run(["uv", "export", "--no-group", "data", "--no-group", "dev", "--format", "requirements.txt"], **KWARGS)
    else:
        contents = subprocess.run(["pip", "freeze"], **KWARGS)

    with open("requirements.txt", "w") as f:
        f.write(contents.stdout)

    subprocess.run(["git", "add", "requirements.txt"], **KWARGS)
