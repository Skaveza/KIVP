import os, sys, shutil, zipfile, subprocess

MODEL_URL = os.getenv("MODEL_URL")
DEST_DIR = "/app/models/layoutlmv3_receipt_model"

if not MODEL_URL:
    print("MODEL_URL not set. Exiting.", file=sys.stderr)
    sys.exit(1)

os.makedirs(DEST_DIR, exist_ok=True)

# Example: download a zip file
zip_path = "/tmp/model.zip"
subprocess.check_call(["curl", "-L", MODEL_URL, "-o", zip_path])

with zipfile.ZipFile(zip_path, "r") as z:
    z.extractall(DEST_DIR)

print("Model downloaded to", DEST_DIR)
