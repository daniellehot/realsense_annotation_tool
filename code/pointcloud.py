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



if __name__=="__main__":
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, COLOR_WIDTH, COLOR_HEIGHT, COLOR_FORMAT, FPS)
    config.enable_stream(rs.stream.depth, DEPTH_WIDTH, DEPTH_HEIGHT, DEPTH_FORMAT, FPS)
    pipe_cfg = pipeline.start(config)

    frames = pipeline.wait_for_frames()
    align = rs.align(rs.stream.color)
    aligned_frames = align.process(frames)
    depth_rs = aligned_frames.get_depth_frame()
    depth_map = np.asarray(depth_rs.get_data())
    color_rs = aligned_frames.get_color_frame()
    color_img = np.asarray(color_rs.get_data())

    pc_rs = rs.pointcloud()
    pc_rs.map_to(color_rs)
    points_rs = rs.points()
    points_rs = pc_rs.calculate(depth_rs)
    v,t = points_rs.get_vertices(), points_rs.get_texture_coordinates()
    verts = np.asarray(v).view(np.float32).reshape((-1, 3))
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(verts)
    o3d.io.write_point_cloud("test.ply", pcd)


    tex_coords = np.asarray(t).view(np.float32).reshape((-1, 2))
    #x_value, y_value = min(max(int(tex_coords*(COLOR_WIDTH, COLOR_HEIGHT) + 0.5), 0))
    u = (tex_coords[:, 0] * COLOR_HEIGHT + 0.5).astype(np.uint32)
    np.clip(u, 0, COLOR_HEIGHT-1, out=u)
    v = (tex_coords[:, 1] * COLOR_WIDTH + 0.5).astype(np.uint32)
    np.clip(v, 0, COLOR_WIDTH-1, out=v)


    pc_colors = color_img[u, v]

#Align Depth to Color:
#Calculate uv map
#result=zero(color frame size)
#foreach pixel (i,j)  in depth frame:
#   (k,l)=uv map(i,j)
    #result(k,l)=min⁡(result(k,l),depth frame(i,j))
    #return result
