import cv2
import os
import pyrealsense2 as rs
from pynput import keyboard
import csv
import numpy as np
import utils


## REALSENSE CONSTANTS ##
COLOR_WIDTH = 1920 #1920
COLOR_HEIGHT = 1080 #1080
COLOR_FORMAT = rs.format.bgr8 #REMEMBER TO SWITCH COLUMNS OF THE COLOR IMAGE BEFORE ADDING COLOR TO A POINT CLOUD 
DEPTH_WIDTH = 1280
DEPTH_HEIGHT = 720
DEPTH_FORMAT = rs.format.z16
FPS = 30
DEPTH_FRAMES_TO_CAPTURE = 20
DEPTH_MIN = 0.5
DEPTH_MAX = 1.5

## CONTROL FLAGS ##
FLAG_PREVIEW = 0
FLAG_SAVE = 0
FLAG_ANNOTATION = 0

## PATH CONSTANTS ##
IMG_PATH = "data/images/"
DEPTH_PATH = "data/depth/"
PC_PATH = "data/pointclouds/"
PC_FILTERED_PATH = "data/pointclouds_filtered"
ANNOTATIONS_PATH = "data/annotations/"
NEW_PATH = "data/new/"
LAST_IMG = None 



def on_press(key):
    global FLAG_PREVIEW, FLAG_SAVE, FLAG_ANNOTATION
    try:
        print('alphanumeric key {0} pressed'.format(key.char))
        #FLAG_KEY = key.char
        if (key.char == "s" and FLAG_PREVIEW == 1):
            FLAG_PREVIEW = 0
            FLAG_SAVE = 1
            FLAG_ANNOTATION = 0
    except AttributeError:
        print('special key {0} pressed'.format(key))


if __name__=="__main__":
    #create_folders()
    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()
    
    #realsense setup
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, COLOR_WIDTH, COLOR_HEIGHT, COLOR_FORMAT, FPS)
    config.enable_stream(rs.stream.depth, DEPTH_WIDTH, DEPTH_HEIGHT, DEPTH_FORMAT, FPS)
    pipeline_cfg = pipeline.start(config)
    align = rs.align(rs.stream.color)

    for i in range(5):
        if i==0:
            print("Waiting for auto-exposure to settle")
        frames = pipeline.wait_for_frames()

    decimation_f = rs.decimation_filter()
    threshold_f = rs.threshold_filter(DEPTH_MIN, DEPTH_MAX)
    spatial_f = rs.spatial_filter()
    temporal_f = rs.temporal_filter()
    depth_to_disparity = rs.disparity_transform(True)
    disparity_to_depth = rs.disparity_transform(False)


    FLAG_PREVIEW = 1
    FLAG_ANNOTATION = 0

    try:
        while True:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()
            if not color_frame or not depth_frame:
                continue
            color_img = np.asanyarray(color_frame.get_data())
            depth_map = np.asanyarray(depth_frame.get_data())
            
            if FLAG_PREVIEW:    
                utils.show_img(color_img)
            
            if FLAG_SAVE:
                cv2.destroyWindow("RealSense")
                LAST_IMG = utils.save_img(color_img, IMG_PATH)

                pc = rs.pointcloud()
                points = rs.points()
                pc.map_to(color_frame)
                points = pc.calculate(depth_frame)
                utils.save_pointcloud(points, color_img, PC_PATH, None)


                depth_frames = utils.collect_depth_frames(pipeline, DEPTH_FRAMES_TO_CAPTURE)
                for frame in depth_frames:
                    frame = decimation_f.process(frame)
                    frame = threshold_f.process(frame)
                    frame = depth_to_disparity.process(frame)
                    frame = spatial_f.process(frame)
                    frame = temporal_f.process(frame)
                    frame = disparity_to_depth.process(frame)
                
                pc_filtered = rs.pointcloud()
                points_filtered = rs.points()
                pc_filtered.map_to(color_frame)
                points_filtered = pc.calculate(depth_frame)
                utils.save_pointcloud(points_filtered, color_img, PC_FILTERED_PATH, "filtered")

                #save_filtered_pointcloud()
                FLAG_PREVIEW = 0
                FLAG_SAVE = 0
                FLAG_ANNOTATION = 1
                
            if FLAG_ANNOTATION:
                annotation_file = NEW_PATH + LAST_IMG + ".csv"
                #print(annotation_file)
                #files = os.listdir(NEW_PATH)
                #if annotation_file in files:
                if os.path.exists(annotation_file):
                    """
                    with open (annotation_file, 'r') as file:
                        reader = csv.DictReader(file)
                        print(reader)
                    """
                    move_files()
                    FLAG_PREVIEW = 1
                    FLAG_SAVE = 0
                    FLAG_ANNOTATION = 0
    except Exception as e: 
        print(e)
    finally:
        pipeline.stop()
        exit(5)