import pyrealsense2 as rs
import numpy as np
import cv2
import open3d as o3d

#https://dev.intelrealsense.com/docs/projection-texture-mapping-and-occlusion-with-intel-realsense-depth-cameras

COLOR_WIDTH = 1920 #1920
COLOR_HEIGHT = 1080 #1080
#COLOR_FORMAT = rs.format.bgr8 #REMEMBER TO SWITCH COLUMNS OF THE COLOR IMAGE BEFORE ADDING COLOR TO A POINT CLOUD 
COLOR_FORMAT = rs.format.rgb8
DEPTH_WIDTH = 1280
DEPTH_HEIGHT = 720
DEPTH_FORMAT = rs.format.z16
FPS = 30


def normalize(x):
    return x.astype(float)/255


if __name__=="__main__":
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, COLOR_WIDTH, COLOR_HEIGHT, COLOR_FORMAT, FPS)
    config.enable_stream(rs.stream.depth, DEPTH_WIDTH, DEPTH_HEIGHT, DEPTH_FORMAT, FPS)
    pipe_cfg = pipeline.start(config)

    for i in range(20):
        if i==0:
            print("Waiting for auto-exposure to settle")
        continue

    frames = pipeline.wait_for_frames()
    align = rs.align(rs.stream.color)
    aligned_frames = align.process(frames)
    
    depth_rs = aligned_frames.get_depth_frame()
    filtered_depth_rs = aligned_frames.get_depth_frame
    depth_map = np.asarray(depth_rs.get_data())

    color_rs = aligned_frames.get_color_frame()
    color_img = np.asarray(color_rs.get_data())

    threshold_f = rs.threshold_filter(0.3, 1.5)
    depth_rs = threshold_f.process(depth_rs)

    pc_rs = rs.pointcloud()
    points_rs = rs.points()
    pc_rs.map_to(color_rs)
    points_rs = pc_rs.calculate(depth_rs)
    v,t = points_rs.get_vertices(), points_rs.get_texture_coordinates()
    verts = np.asarray(v).view(np.float32).reshape((-1, 3))
    print(verts.shape)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(verts)
    o3d.io.write_point_cloud("test_geometry.ply", pcd)


    #Read normalized UV map
    tex_coords = np.asarray(t).view(np.float32).reshape((-1, 2))
    print(tex_coords.shape)
    #Perform UV mapping, where V stands for the HEIGHT and U for the WIDTH
    #SOURCE - http://docs.ros.org/en/kinetic/api/librealsense2/html/opencv__pointcloud__viewer_8py_source.html L255-258
    #SOURCE - https://github.com/IntelRealSense/librealsense/blob/master/wrappers/pcl/pcl-color/rs-pcl-color.cpp L66
    
    u = (tex_coords[:, 0] * COLOR_WIDTH + 0.5).astype(np.uint32)
    np.clip(u, 0, COLOR_WIDTH-1, out=u)
    v = (tex_coords[:, 1] * COLOR_HEIGHT + 0.5).astype(np.uint32)
    np.clip(v, 0, COLOR_HEIGHT-1, out=v)
    
    #v, u = (tex_coords * (COLOR_WIDTH, COLOR_HEIGHT) + 0.5).astype(np.uint32).T
    #np.clip(u, 0, COLOR_HEIGHT-1, out=u)
    #np.clip(v, 0, COLOR_WIDTH-1, out=v)

    #Read normalized colors from the color source, in this image color image
    #Colors must be normalized because open3d expects colors values to be floats in range 0 to 1
    color_img_normalized = normalize(color_img)
    pc_colors = color_img_normalized[v, u]

    #Insert colors to the point cloud
    pcd.colors = o3d.utility.Vector3dVector(pc_colors)
    o3d.io.write_point_cloud("test_RGB.ply", pcd)
    o3d.visualization.draw_geometries([pcd])

