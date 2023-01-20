#TODO https://github.com/IntelRealSense/librealsense/issues/7747
#TODO https://github.com/IntelRealSense/librealsense/issues/5403
#TODO https://github.com/IntelRealSense/librealsense/tree/master/examples/pointcloud
#TODO https://github.com/IntelRealSense/librealsense/blob/master/wrappers/python/examples/opencv_pointcloud_viewer.py
#TODO https://github.com/IntelRealSense/realsense-ros/issues/41 

#http://docs.ros.org/en/kinetic/api/librealsense2/html/rs-pcl-color_8cpp_source.html

import cv2
import os
import pyrealsense2 as rs
from pynput import keyboard
import csv
import numpy as np


COLOR_WIDTH = 1920 #1280 
COLOR_HEIGHT = 1080 #720 
COLOR_FORMAT = rs.format.bgr8
DEPTH_WIDTH = 1280
DEPTH_HEIGHT = 720
DEPTH_FORMAT = rs.format.z16
FPS = 30

FLAG_PREVIEW = 0
FLAG_SAVE = 0
FLAG_ANNOTATION = 0
#FLAG_KEY = "None"

IMG_PATH = "data/images/"
DEPTH_PATH = "data/depth/"
PC_PATH = "data/pointclouds/"
ANNOTATIONS_PATH = "data/annotations/"
NEW_PATH = "data/new/"
LAST_IMG = None

# TODO remove this function
def create_folders():
    if not os.path.exists("data"):
        os.mkdir("data")
        os.mkdir("data/images")
        os.mkdir("data/depth")
        os.mkdir("data/new")
        os.mkdir("data/pointclouds")
        os.mkdir("data/annotations")


def on_press(key):
    global FLAG_PREVIEW, FLAG_SAVE, FLAG_ANNOTATION
    try:
        print('alphanumeric key {0} pressed'.format(key.char))
        #FLAG_KEY = key.char
        if (key.char == "s" and FLAG_PREVIEW == 1):
            FLAG_PREVIEW = 0
            FLAG_SAVE = 1
            FLAG_ANNOTATION = 0
        #if (key.char == "p"):
        #    FLAG_PREVIEW = 1
        #    FLAG_SAVE = 0
        #    FLAG_ANNOTATION = 0
    except AttributeError:
        print('special key {0} pressed'.format(key))


def setup_realsense_pipeline():
    pipeline = rs.pipeline()
    config = rs.config()
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    config.enable_stream(rs.stream.color, COLOR_WIDTH, COLOR_HEIGHT, COLOR_FORMAT, FPS)
    config.enable_stream(rs.stream.depth, DEPTH_WIDTH, DEPTH_HEIGHT, DEPTH_FORMAT, FPS)
    cfg = pipeline.start(config)
    align_to = rs.stream.color
    align = rs.align(align_to)

    profile = cfg.get_stream(rs.stream.color)
    color_intrinsics = profile.as_video_stream_profile().get_intrinsics()
    profile = cfg.get_stream(rs.stream.depth)
    depth_intrinsics = profile.as_video_stream_profile().get_intrinsics()
    return pipeline, align, color_intrinsics, depth_intrinsics


def get_filename(path):
    number_of_files = len(os.listdir(path))
    #print(number_of_files)
    number_of_files += 1
    number_of_files = str(number_of_files).zfill(5)
    return  number_of_files


def save_img(img):
    global LAST_IMG
    #print("save_data")
    filename = get_filename(IMG_PATH)
    #img_path = "data/images/" + filename + '.png'
    img_path = "data/new/" + filename + ".png"
    LAST_IMG = filename
    cv2.imwrite(img_path, img)
    print("Image saved")

def save_depth(map):
    filename = get_filename(DEPTH_PATH)
    depth_path = "data/new/" + filename + ".npy"
    np.save(depth_path, map)
    #depth_path = "data/new/" + filename + ".csv"
    #np.savetxt(depth_path, map, delimiter = ',')
    print("Depth map saved")


def save_pointcloud(depth_frame, color_frame):
    pc = rs.pointcloud()
    points = rs.points()

    points = pc.calculate(depth_frame)
    #print(points)
    tex_coords = points.get_texture_coordinates()
    v = points.get_vertices()
    verts = np.asanyarray(v).view(np.float32).reshape(-1, 3)  # xyz
    print(verts)
    print(verts.shape)
    #print(tex_coords)
    #print(tex_coords)
    pc.map_to(color_frame)

    filename = get_filename(PC_PATH)
    #pc_path = "data/pointclouds/" + filename + ".ply"
    pc_path = "data/new/" + filename + ".ply"
    points.export_to_ply(pc_path, color_frame)
    print("Pointcloud saved")


def show_img(img):
    scaled_img = cv2.resize(img, (1280, 720))
    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('RealSense', scaled_img)
    cv2.waitKey(1)


def move_files():
    os.rename(NEW_PATH + LAST_IMG + ".png", IMG_PATH + LAST_IMG + ".png")
    os.rename(NEW_PATH + LAST_IMG + ".npy", DEPTH_PATH + LAST_IMG + ".npy")
    os.rename(NEW_PATH + LAST_IMG + ".ply", PC_PATH + LAST_IMG + ".ply")
    os.rename(NEW_PATH + LAST_IMG + ".csv", ANNOTATIONS_PATH + LAST_IMG + ".csv")


"""
def convert_pixel_to_point(file, intrinsics):
    pixel = read from file
    depth = rs.get_depth(pixel)
    point = rs.rs2_deproject_pixel_to_point(intrinsics, pixel, depth)
    return point
"""


if __name__=="__main__":
    #create_folders()

    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()
    
    pipeline, align, color_i, depth_i = setup_realsense_pipeline()
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
            #depth_map = np.asanyarray(depth_frame.get_data())
            depth_map = np.asanyarray(depth_frame.get_data(), dtype=float) #depth in milimeters
            #print(depth_map.shape)
            #print(depth_map)
            #print(depth_frame.get_distance(50, 20)) #NOTE COLUMN FIRST
            #print(depth_map[20, 50]) #NOTE ROW FIRST
            #exit(5)

            if FLAG_PREVIEW:    
                show_img(color_img)
            
            if FLAG_SAVE:
                cv2.destroyWindow("RealSense")
                save_img(color_img)
                save_depth(depth_map)
                save_pointcloud(depth_frame, color_frame)
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
        