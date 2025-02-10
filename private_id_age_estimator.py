import csv
import os
import sys
import time

from cryptonets_python_sdk.factor import FaceFactor
from cryptonets_python_sdk.settings.loggingLevel import LoggingLevel
from tqdm import tqdm

server_url = "https://api.cryptonets.ai/node"
api_key = "accsb18b5f17d924db88"


def list_images(base_path):
    # loop over the directory structure
    image_types = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")
    for (rootDir, dirNames, filenames) in os.walk(base_path):
        # loop over the filenames in the current directory
        for filename in filenames:
            # determine the file extension of the current file
            ext = filename[filename.rfind("."):].lower()
            # check to see if the file is an image and should be processed
            if ext.endswith(image_types):
                # construct the path to the image and yield it
                imagePath = os.path.join(rootDir, filename)
                yield imagePath


if __name__ == "__main__":
    face_factor = FaceFactor(server_url=server_url, api_key=api_key, logging_level=LoggingLevel.off)

    image_folder_path = sys.argv[1]
    image_path_list = list(list_images(image_folder_path))
    print("Processing {} images".format(len(image_path_list)))

    with open(f'result_{time.time_ns()}.csv', 'w', newline='') as csvfile:
        fieldnames = ['image_path', 'error', 'message', 'return_code', 'return_message', 'age']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for image_path in tqdm(image_path_list):
            age_handle = face_factor.estimate_age(image_path=image_path)
            age_result = {"image_path": image_path.replace(image_folder_path, ""), "error": age_handle.error,
                          "message": age_handle.message}
            for index, face in enumerate(age_handle.face_objects):
                age_face_result = {"return_code": face.return_code, "return_message": face.message, "age": face.age}
                age_face_result = age_result | age_face_result
                writer.writerow(age_face_result)
