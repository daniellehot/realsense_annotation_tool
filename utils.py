import os
import time
import cv2

def scan_for_new_files(path):
    files = []
    while 1:
        files = os.listdir(path)
        print("No new image")
        #print(files)
        if len(files) != 0:
            break;
        time.sleep(1.0)
    image_path = os.path.join(path, files[0])
    return image_path