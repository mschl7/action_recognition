import zipfile
import cv2
from pathlib import Path
import tempfile
import random
import shutil

"""
    Extract single frame from videos. 
    Change frame_pos to decide which frames gets saved.
    Change OUTPUT_FOLDER name.
"""

##### change befor executing #####

OUTPUT_FOLDER = Path("end_frame")    
frame_pos = 4/4  # as franction

##################################

# folder paths
INPUT_FOLDER = Path("../action_recognition_data")     
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# params for splitting
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15
random.seed(42)  

# needed for working with model
class_rename = { 
    "capitulate": "class1",
    "clapping": "class2",
    "cross_arms": "class3",
    "hand_waving": "class4"
}

# output folders
for split in ["train", "val", "test"]:
    for class_name in class_rename.values():
        (OUTPUT_FOLDER / split / class_name).mkdir(
            parents=True,
            exist_ok=True
        )

# extract frame from each video 
successful = 0
with tempfile.TemporaryDirectory() as temp_dir:

    temp_dir = Path(temp_dir)
    zip_files = list(INPUT_FOLDER.glob("*.zip"))

    # store by class
    images_by_class = {
        class_name: []
        for class_name in class_rename
    }

    for zip_path in zip_files:
        print(f"\nProcessing: {zip_path.name}")

        # temp directory
        extract_dir = temp_dir / zip_path.stem
        extract_dir.mkdir(parents=True, exist_ok=True)

        # extract zip
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        # get avi files
        avi_files = list(extract_dir.rglob("*.avi"))

        for video_path in avi_files:

            # find class
            relative_path = video_path.relative_to(extract_dir)
            class_name = relative_path.parts[0]

            # open video
            cap = cv2.VideoCapture(str(video_path))

            # count frames
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Frame position in video
            frame_position = int(frame_count * frame_pos)
            frame_position = min(frame_position, frame_count - 1) #check pos


            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
            success_read, frame = cap.read()
            cap.release()

            # save temp images
            temp_class_dir = (temp_dir /"frames" / class_name)
            temp_class_dir.mkdir(parents=True, exist_ok=True)
            output_name = (video_path.stem + "_ending.jpg")
            output_path = (temp_class_dir / output_name)
            cv2.imwrite(str(output_path), frame)
            images_by_class[class_name].append( output_path)

            successful += 1

    print("SPLITTING DATA")
    for class_name, images in images_by_class.items():

        random.shuffle(images)
        n = len(images)
        train_end = int(n * TRAIN_RATIO)
        val_end = train_end + int(n * VAL_RATIO)
        train_images = images[:train_end]
        val_images = images[train_end:val_end]
        test_images = images[val_end:]

        print(f"\n{class_name}")
        print(f"Total: {n}")
        print(f"Train: {len(train_images)}")
        print(f"Val:   {len(val_images)}")
        print(f"Test:  {len(test_images)}")

        output_class = class_rename[class_name]
        for image in train_images:
            shutil.copy2(
                image,
                OUTPUT_FOLDER /
                "train" /
                output_class /
                image.name)

        for image in val_images:
            shutil.copy2(
                image,
                OUTPUT_FOLDER /
                "val" /
                output_class /
                image.name)
            
        for image in test_images:
            shutil.copy2(
                image,
                OUTPUT_FOLDER /
                "test" /
                output_class /
                image.name)

print("DONE")
print(f"Frames extracted: {successful}")


