import csv
import random
import shutil
import tempfile
import zipfile
from pathlib import Path
import cv2


"""
    - Extract frames from videos at 8 FPS
    - change to 224x224 format
    - Split in train, test and val
    - Saved in data/ video_frames_data
"""

#folders
PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_FOLDER = Path("../action_recognition_data")     
OUTPUT_FOLDER = (
    PROJECT_ROOT /
    "data" /
    "video_frames_data"
)

# settings
FPS = 8
IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15
random.seed(42)

# needed for working model
CLASS_RENAME = {
    "capitulate": "class1",
    "clapping": "class2",
    "cross_arms": "class3",
    "hand_waving": "class4"
}

CLASS_TO_ID = {
    "class1": 0,
    "class2": 1,
    "class3": 2,
    "class4": 3
}

#output folders
for split in ["train", "val", "test"]:
    for class_name in CLASS_RENAME.values():
        (OUTPUT_FOLDER / split / class_name).mkdir(
            parents=True,
            exist_ok=True
        )

# get frames
def extract_frames(video_path, output_dir):
    output_dir.mkdir(
        parents=True,
        exist_ok=True)

    video = cv2.VideoCapture(str(video_path))

    original_fps = video.get(cv2.CAP_PROP_FPS)

    # get approximately 8 FPS
    frame_interval = original_fps / FPS
    next_frame_to_save = 0.0
    frame_number = 0
    saved_frames = 0

    while True:
        success, frame = video.read()

        if not success:
            break

        # save frames at approximately 8 FPS
        if frame_number >= next_frame_to_save:

            # resize 
            frame = cv2.resize(
                frame,
                (
                    IMAGE_WIDTH,
                    IMAGE_HEIGHT
                ),
                interpolation=cv2.INTER_AREA
            )

            output_path = (
                output_dir /
                f"frame_{saved_frames + 1:05d}.jpg"
            )

            cv2.imwrite(
                str(output_path),
                frame,
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    95
                ]
            )

            saved_frames += 1
            next_frame_to_save += frame_interval
        frame_number += 1
    video.release()

    if saved_frames == 0:
        return False
    return True

# split
def split_videos(videos):

    videos = list(videos)
    random.shuffle(videos)
    number_of_videos = len(videos)

    train_count = int(number_of_videos * TRAIN_RATIO)
    val_count = int(number_of_videos * VAL_RATIO)
    train_videos = videos[:train_count]
    val_videos = videos[train_count:train_count + val_count]
    test_videos = videos[train_count + val_count:]

    return {
        "train": train_videos,
        "val": val_videos,
        "test": test_videos
    }

def count_frames(frame_directory):

    return len(
        list(
            frame_directory.glob(
                "frame_*.jpg"
            )
        )
    )


total_videos = 0
successful_videos = 0
failed_videos = 0

metadata_rows = []

#temps for zips
with tempfile.TemporaryDirectory() as temp:

    temp_dir = Path(temp)
    zip_files = sorted(INPUT_FOLDER.glob("*.zip"))

    for zip_path in zip_files:

        original_class = (zip_path.stem.lower())
        class_name = CLASS_RENAME[original_class]
        class_id = CLASS_TO_ID[class_name]

        extract_dir = (
            temp_dir /
            original_class
        )

        extract_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as zip_file:
            zip_file.extractall(
                extract_dir
            )

        videos = list(extract_dir.rglob("*.avi"))
        videos += list(extract_dir.rglob("*.AVI"))
        videos = sorted(set(videos))

        #split
        splits = split_videos(videos)

        for split, split_videos_list in splits.items():
            class_output_dir = (
                OUTPUT_FOLDER /
                split /
                class_name
            )

            for video_path in split_videos_list:
                total_videos += 1
                video_name = (video_path.stem)

                video_output_dir = (
                    class_output_dir /
                    video_name
                )

                success = extract_frames(
                    video_path,
                    video_output_dir
                )

                if not success:
                    failed_videos += 1
                    if video_output_dir.exists():
                        shutil.rmtree(
                            video_output_dir
                        )
                    continue

                num_frames = count_frames(video_output_dir)


                if num_frames == 0:
                    failed_videos += 1
                    shutil.rmtree(
                        video_output_dir
                    )
                    continue

                successful_videos += 1

                relative_frame_dir = (
                    video_output_dir
                    .relative_to(
                        OUTPUT_FOLDER
                    )
                )

                # Metadata                
                metadata_rows.append({
                    "video_id": video_name,
                    "original_class": original_class,
                    "class_name":class_name,
                    "class_id":class_id,
                    "split":split,
                    "frame_dir":str(relative_frame_dir),
                    "num_frames":num_frames,
                    "fps":FPS,
                    "width":IMAGE_WIDTH,
                    "height":IMAGE_HEIGHT
                })

# write metadata
metadata_file = (
    OUTPUT_FOLDER /
    "metadata.csv"
)

with open(
    metadata_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    fieldnames = [
        "video_id",
        "original_class",
        "class_name",
        "class_id",
        "split",
        "frame_dir",
        "num_frames",
        "fps",
        "width",
        "height"
    ]
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )
    writer.writeheader()
    writer.writerows(
        metadata_rows
    )


print("Done!")
print(metadata_file)