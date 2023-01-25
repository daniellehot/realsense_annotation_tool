import cv2
import pyrealsense2 as rs
import numpy as np
import open3d as o3d
import os


def deproject_pixel_to_point(pixel_row, pixel_col, depth, intrinsics):
    print(intrinsics)
    print(pixel_row)
    print(pixel_col)
    print(depth)
    point = [0, 0, 0]
    #points = np.zeros((15, 3)).astype(np.float16)
    cx = intrinsics.ppx
    cy = intrinsics.ppy
    fx = intrinsics.fx
    fy = intrinsics.fy
    point[0] = ((pixel_col - cx) * depth)/fx
    point[1] = ((pixel_row - cy) * depth)/fy
    point[2] = depth 
    point = np.asarray(point).astype(np.float16)
    return point.T


def collect_depth_frames(pipeline, frames_to_capture):
    depth_set = []
    for i in range(frames_to_capture):
        if i==0: 
            print("Collecting depth set")
        frames = pipeline.wait_for_frames()
        align = rs.align(rs.stream.color)
        aligned_frames = align.process(frames)
        depth_rs = aligned_frames.get_depth_frame()
        depth_set.append(depth_rs)
    return depth_set


def normalize(x):
        return x.astype(float)/255


def save_pointcloud(points_rs, color_img, path, filtered):
    v,t = points_rs.get_vertices(), points_rs.get_texture_coordinates()
    verts = np.asarray(v).view(np.float32).reshape((-1, 3))
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(verts)
    
    #Read normalized UV map
    tex_coords = np.asarray(t).view(np.float32).reshape((-1, 2))
    #Perform UV mapping, where V stands for the HEIGHT and U for the WIDTH
    #SOURCE - http://docs.ros.org/en/kinetic/api/librealsense2/html/opencv__pointcloud__viewer_8py_source.html L255-258
    #SOURCE - https://github.com/IntelRealSense/librealsense/blob/master/wrappers/pcl/pcl-color/rs-pcl-color.cpp L66
    color_width = color_img.shape[1]
    color_height = color_img.shape[0]
    u = (tex_coords[:, 0] * color_width + 0.5).astype(np.uint32)
    np.clip(u, 0, color_width-1, out=u)
    v = (tex_coords[:, 1] * color_height + 0.5).astype(np.uint32)
    np.clip(v, 0, color_height-1, out=v)

    #Read normalized colors from the color source, in this image color image
    #Colors must be normalized because open3d expects colors values to be floats in range 0 to 1
    color_img_normalized = normalize(color_img)
    pc_colors = color_img_normalized[v, u]
    #Insert colors to the point cloud
    pcd.colors = o3d.utility.Vector3dVector(pc_colors)
    
    filename = get_filename(path)
    #pc_path = "data/pointclouds/" + filename + ".ply"
    pc_path = "data/new/" + filename + ".ply"
    if filtered == "filtered":
        pc_path = "data/new/" + filename + "_filtered.ply"
    o3d.io.write_point_cloud(pc_path, pcd)

    if filtered == "filtered":
        print("Filtered pointcloud saved")
    else:
        print("Pointcloud saved")
    #o3d.io.write_point_cloud("test_RGB.ply", pcd)
    #o3d.visualization.draw_geometries([pcd, annotations_pc])


def save_img(img, path):
    #print("save_data")
    filename = get_filename(path)
    #img_path = "data/images/" + filename + '.png'
    img_path = "data/new/" + filename + ".png"
    #LAST_IMG = filename
    cv2.imwrite(img_path, img)
    print("Image saved")
    return filename


def create_folders():
    if not os.path.exists("data"):
        os.mkdir("data")
        os.mkdir("data/images")
        os.mkdir("data/depth")
        os.mkdir("data/new")
        os.mkdir("data/pointclouds")
        os.mkdir("data/annotations")


def show_img(img):
    scaled_img = cv2.resize(img, (1280, 720))
    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('RealSense', scaled_img)
    cv2.waitKey(1)


def get_filename(path):
    number_of_files = len(os.listdir(path))
    #print(number_of_files)
    number_of_files += 1
    number_of_files = str(number_of_files).zfill(5)
    return  number_of_files
