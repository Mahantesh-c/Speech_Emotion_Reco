"""
Script to download and organize RAVDESS, TESS, and EMOVO datasets for speech emotion recognition.
- RAVDESS and TESS will be downloaded and extracted automatically.
- EMOVO will provide instructions for manual download due to license restrictions.

Run this script from the root of your project:
    python download_datasets.py
"""
import os
import sys
import zipfile
import requests
from pathlib import Path

DATASETS_DIR = Path('datasets')

RAVDESS_URL = 'https://zenodo.org/record/1188976/files/Audio_Speech_Actors_01-24.zip?download=1'
RAVDESS_ZIP = DATASETS_DIR / 'ravdess.zip'
RAVDESS_DIR = DATASETS_DIR / 'ravdess'

TESS_URL = 'https://tspace.library.utoronto.ca/bitstream/1807/24487/1/TESS%20Toronto%20emotional%20speech%20set%20data.zip'
TESS_ZIP = DATASETS_DIR / 'tess.zip'
TESS_DIR = DATASETS_DIR / 'tess'

EMOVO_DIR = DATASETS_DIR / 'emovo'
EMOVO_INSTRUCTIONS = EMOVO_DIR / 'README.txt'


def download_file(url, dest):
    if dest.exists():
        print(f"{dest} already exists, skipping download.")
        return
    print(f"Downloading {url} ...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded to {dest}")

def extract_zip(zip_path, extract_to):
    print(f"Extracting {zip_path} ...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Extracted to {extract_to}")

def setup_emovo():
    EMOVO_DIR.mkdir(parents=True, exist_ok=True)
    if not EMOVO_INSTRUCTIONS.exists():
        with open(EMOVO_INSTRUCTIONS, 'w') as f:
            f.write(
                "EMOVO dataset must be downloaded manually due to license restrictions.\n"
                "Visit https://voice.fub.it/activities/emovo/ and follow the instructions to download.\n"
                "After downloading, extract the contents into this folder.\n"
            )
    print(f"EMOVO instructions written to {EMOVO_INSTRUCTIONS}")

def main():
    DATASETS_DIR.mkdir(exist_ok=True)
    # RAVDESS
    download_file(RAVDESS_URL, RAVDESS_ZIP)
    if not RAVDESS_DIR.exists() or not any(RAVDESS_DIR.iterdir()):
        extract_zip(RAVDESS_ZIP, RAVDESS_DIR)
    else:
        print(f"{RAVDESS_DIR} already extracted.")
    # TESS
    download_file(TESS_URL, TESS_ZIP)
    if not TESS_DIR.exists() or not any(TESS_DIR.iterdir()):
        extract_zip(TESS_ZIP, TESS_DIR)
    else:
        print(f"{TESS_DIR} already extracted.")
    # EMOVO
    setup_emovo()
    print("\nAll datasets are set up. If you see a README.txt in the emovo folder, follow its instructions to complete EMOVO setup.")

if __name__ == "__main__":
    main()
