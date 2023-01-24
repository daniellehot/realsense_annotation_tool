import cv2 as cv
import numpy as np
import pyrealsense2 as rs
import open3d as o3d

COLOR_WIDTH = 1280 #1920
COLOR_HEIGHT = 720 #1080
COLOR_FORMAT = rs.format.bgr8
DEPTH_WIDTH = 1280
DEPTH_HEIGHT = 720
DEPTH_FORMAT = rs.format.z16
FPS = 30


IMG_PATH = "data/images/00003.png"
DEPTH_PATH = "data/depth/00003.npy"

def convert_depth_to_coord(x, y, depth, intrinsics):
    depth /= 1000
    P = rs.rs2_deproject_pixel_to_point(intrinsics, [x, y], depth)  #result[0]: right, result[1]: down, result[2]: forward
    return P

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

    depth_sensor = cfg.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()
    print("depth scale", depth_scale)
    return pipeline, align, color_intrinsics, depth_intrinsics


if __name__=="__main__":
    pipeline, align, color_intrinsics, depth_intrinsics = setup_realsense_pipeline()
    print(color_intrinsics)
    #print(depth_intrinsics)
    img = cv.imread(IMG_PATH)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    #print(img.shape)
    #depth = np.load(DEPTH_PATH)
    #depth_fixed = depth.astype(float)

    frames = pipeline.wait_for_frames()
    aligned_frames = align.process(frames)
    color_frame = aligned_frames.get_color_frame()
    depth_frame = aligned_frames.get_depth_frame()

    depth = np.asanyarray(depth_frame.get_data(), dtype=float)

    #print(depth.shape)
    pointcloud_size = depth.shape[0]*depth.shape[1]
    rgb_pc = np.zeros((pointcloud_size, 6))

    for x in range(COLOR_WIDTH):
        for y in range(COLOR_HEIGHT):
            point_idx = x*y
            rgb_pc[point_idx, :3] = convert_depth_to_coord(x, y, depth[y, x], color_intrinsics)
            rgb_pc[point_idx, 3:] = img[y, x, :] 
    print(rgb_pc.shape)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(rgb_pc[:, :3])
    o3d.io.write_point_cloud("test.ply", pcd)

    #pcd.colors = o3d.utility.Vector3dVector(rgb_pc[:, 3:])
    #o3d.visualization.draw_geometries([pcd])
    #pcd.points = rgb_pc[:, :3]
    #pcd.colors = rgb_pc[:, 3:]



