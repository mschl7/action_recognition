from pathlib import Path
import zipfile
import shutil


""" 
Processes zip folders and copies only the ones with right action ID.

Saved videos overall:
    nturgbd_rgb_s001.zip -> 144 videos
    nturgbd_rgb_s002.zip -> 162 videos
    nturgbd_rgb_s003.zip -> 162 videos
    nturgbd_rgb_s004.zip -> 72 videos
    nturgbd_rgb_s005.zip -> 144 videos
    nturgbd_rgb_s006.zip -> 180 videos
    nturgbd_rgb_s007.zip -> 216 videos
    nturgbd_rgb_s008.zip -> 252 videos
    nturgbd_rgb_s009.zip -> 126 videos
    nturgbd_rgb_s010.zip -> 180 videos
    nturgbd_rgb_s011.zip -> 234 videos
    nturgbd_rgb_s012.zip -> 198 videos
    nturgbd_rgb_s013.zip -> 198 videos
    nturgbd_rgb_s014.zip -> 162 videos
    nturgbd_rgb_s015.zip -> 144 videos
    nturgbd_rgb_s016.zip -> 126 videos
    nturgbd_rgb_s017.zip -> 144 videos
                            

    nturgbd_rgb_s018.zip -> 36 videos
    nturgbd_rgb_s019.zip -> 54 videos
    nturgbd_rgb_s020.zip -> 42 videos
    nturgbd_rgb_s021.zip -> 36 videos
    nturgbd_rgb_s022.zip -> 42 videos
    nturgbd_rgb_s023.zip -> 84 videos
    nturgbd_rgb_s024.zip -> 42 videos
    nturgbd_rgb_s025.zip -> 42 videos
    nturgbd_rgb_s026.zip -> 84 videos
    nturgbd_rgb_s027.zip -> 90 videos
    nturgbd_rgb_s028.zip -> 54 videos
    nturgbd_rgb_s029.zip -> 90 videos
    nturgbd_rgb_s030.zip -> 108 videos
    nturgbd_rgb_s031.zip -> 96 videos
    nturgbd_rgb_s032.zip -> 60 videos
"""

ACTIONS = {
    "A040": "cross_arms",
    "A010": "clapping",
    "A023": "hand_waving",   
    "A095": "capitulate"
}

DOWNLOAD_DIR = Path("downloads")
OUTPUT_DIR = Path("dataset")
TEMP_DIR = Path("temp_extract")


#create folders
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# go through downloaded zip files
zip_files = sorted(DOWNLOAD_DIR.glob("*.zip"))

for zip_file in zip_files:

    print(f"Processing: {zip_file.name}")

    # Clean temp folder
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.mkdir()

    # extract ZIP
    print("Extracting...")

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(TEMP_DIR)

    # count how many videos are copied from zip
    copied = 0

    # Find videos with right codes and save
    for video in TEMP_DIR.rglob("*_rgb.avi"):
        filename = video.name
        action_id = filename.split("A")[-1][:3]
        action_id = "A" + action_id

        if action_id in ACTIONS:

            action_name = ACTIONS[action_id]
            destination = OUTPUT_DIR / action_name
            destination.mkdir(
                parents=True,
                exist_ok=True)

            shutil.copy2(
                video,
                destination / filename)

            copied += 1

    print(f"Copied {copied} videos")
    # remove extracted files
    print("Cleaning temporary files...")
    shutil.rmtree(TEMP_DIR)

print("\ Done")
