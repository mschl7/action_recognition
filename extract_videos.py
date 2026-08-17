import os
import random
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

# folders
INPUT_FOLDER = Path("../action_recognition_data")
OUTPUT_FOLDER = Path("/data/video_frames_data")

# image format
FPS = 8
IMAGE_SIZE = "224:224"

# params for splitting
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

random.seed(42)  

# needed for working with model
CLASS_RENAME = {
    "capitulate": "class1",
    "clapping": "class2",
    "cross_arms": "class3",
    "hand_waving": "class4"
}

# output folder
for split in ["train", "val", "test"]:
    for class_name in CLASS_RENAME.values():
        output_dir = (
            OUTPUT_FOLDER /
            split /
            class_name)
        output_dir.mkdir(parents=True, exist_ok=True)


# extract frames
def extract_frames(video_path, output_dir, video_name):

    output_dir.mkdir(
        parents=True,
        exist_ok=True)

    # add the video name 
    output_pattern = (
        output_dir /
        f"{video_name}_img_%05d.jpg")

    cmd = [
        "ffmpeg",
        "-i",
        str(video_path),
        "-vf",
        f"fps={FPS},scale={IMAGE_SIZE},format=yuv420p",
        "-q:v",
        "2",
        str(output_pattern)
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        return True

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed for: {video_path}")
        print(e.stderr.decode(errors="ignore"))
        return False

# process zips
total_videos = 0
successful_videos = 0
with tempfile.TemporaryDirectory() as temp:

    temp_dir = Path(temp)
    zip_files = list(INPUT_FOLDER.glob("*.zip"))

    for zip_path in zip_files:
        # get class
        class_name = zip_path.stem.lower()
        output_class = CLASS_RENAME[class_name]

        # temp dirs
        extract_dir = (
            temp_dir /
            class_name)

        extract_dir.mkdir(
            parents=True,
            exist_ok=True)


        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as zip_ref:
                zip_ref.extractall(
                extract_dir)
        # split videos
        videos = list(extract_dir.rglob("*.avi"))
        random.shuffle(videos)
        n = len(videos)

        train_end = int(n * TRAIN_RATIO)
        val_end = (train_end + int(n * VAL_RATIO))
        train_videos = videos[:train_end]
        val_videos = videos[train_end:val_end]
        test_videos = videos[val_end:]

        splits = {
            "train": train_videos,
            "val": val_videos,
            "test": test_videos
        }
        print( f"Train: {len(train_videos)}")
        print( f"Val:   {len(val_videos)}")
        print(f"Test:  {len(test_videos)}")


        #extract frames
        for split, split_videos in splits.items():
            output_dir = (
                OUTPUT_FOLDER /
                split /
                output_class)

            for video_path in split_videos:

                total_videos += 1

                # Remove problematic characters
                # from the video filename
                video_name = video_path.stem

                print(
                    f"\n[{split}] "
                    f"{class_name}: "
                    f"{video_name}"
                )


                success = extract_frames(
                    video_path,
                    output_dir,
                    video_name
                )


                if success:

                    successful_videos += 1


print("DONE")

print(
    f"Videos processed: "
    f"{total_videos}"
)

print(
    f"Successful: "
    f"{successful_videos}"
)

print(
    f"Dataset saved to:"
)

print(
    OUTPUT_FOLDER.resolve()
)