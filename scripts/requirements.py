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

has_uv = shutil.which("uv") is not None

if has_uv:
    contents = subprocess.run(["uv", "export", "--format", "requirements.txt"], **KWARGS)
else:
    contents = subprocess.run(["pip", "freeze"], **KWARGS)

with open("requirements.txt", "w") as f:
    f.write(contents.stdout)

subprocess.run(["git", "add", "requirements.txt"], **KWARGS)
