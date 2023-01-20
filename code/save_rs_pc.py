import pyrealsense2 as rs
import numpy as np
import cv2
import open3d as o3d


COLOR_WIDTH = 1920 #1920
COLOR_HEIGHT = 1080 #1080
COLOR_FORMAT = rs.format.bgr8
DEPTH_WIDTH = 1280
DEPTH_HEIGHT = 720
DEPTH_FORMAT = rs.format.z16
FPS = 30

#http://docs.ros.org/en/kinetic/api/librealsense2/html/opencv__pointcloud__viewer_8py_source.html


def create_RGB_pointcloud(points_rs, color_rs):
    v, t = points_rs.get_vertices(), points_rs.get_texture_coordinates()
    #tex_coords = np.asanyarray(points_rs.get_texture_coordinates())
    #verts = np.asanyarray(points_rs.get_vertices())
    verts = np.asanyarray(v)  # xyz
    tex_coords = np.asanyarray(t)  # uv
    
    
    print(tex_coords.size)
    print(verts.size)
    XYZ, RGB = [], []
    print(tex_coords[305222])
    print(verts[305222])

    #for i in range(points_rs.size()):
    #    print(verts[i])



if __name__=="__main__":
    pipeline = rs.pipeline()
    config = rs.config()
    pc_rs = rs.pointcloud()
    #pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    #pipeline_profile = config.resolve(pipeline_wrapper)
    #device = pipeline_profile.get_device()
    config.enable_stream(rs.stream.color, COLOR_WIDTH, COLOR_HEIGHT, COLOR_FORMAT, FPS)
    config.enable_stream(rs.stream.depth, DEPTH_WIDTH, DEPTH_HEIGHT, DEPTH_FORMAT, FPS)
    pipe_cfg = pipeline.start(config)
    #align_to = rs.stream.color
    #align = rs.align(align_to)
    #profile = cfg.get_stream(rs.stream.color)
    #color_intrinsics = profile.as_video_stream_profile().get_intrinsics()
    #profile = cfg.get_stream(rs.stream.depth)
    #depth_intrinsics = profile.as_video_stream_profile().get_intrinsics()
    #depth_sensor = cfg.get_device().first_depth_sensor()
    #depth_scale = depth_sensor.get_depth_scale()
    #print("depth scale", depth_scale)
    frames = pipeline.wait_for_frames()
    depth_rs = frames.get_depth_frame()
    color_rs = frames.get_color_frame()
    pc_rs.map_to(color_rs)
    points_rs = rs.points()
    points_rs = pc_rs.calculate(depth_rs)
    create_RGB_pointcloud(points_rs, color_rs)
