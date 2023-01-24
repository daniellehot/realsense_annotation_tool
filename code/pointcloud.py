import pyrealsense2 as rs
import numpy as np
import cv2
import open3d as o3d

#https://dev.intelrealsense.com/docs/projection-texture-mapping-and-occlusion-with-intel-realsense-depth-cameras

COLOR_WIDTH = 1920 #1920
COLOR_HEIGHT = 1080 #1080
COLOR_FORMAT = rs.format.bgr8 #REMEMBER TO SWITCH COLUMNS OF THE COLOR IMAGE BEFORE ADDING COLOR TO A POINT CLOUD 
#COLOR_FORMAT = rs.format.rgb8
DEPTH_WIDTH = 1280
DEPTH_HEIGHT = 720
DEPTH_FORMAT = rs.format.z16
FPS = 30
DEPTH_FRAMES_TO_CAPTURE = 20
DEPTH_MIN = 0.5
DEPTH_MAX = 1.5

#FILTERING TUTORIAL PYTHON https://github.com/IntelRealSense/librealsense/blob/jupyter/notebooks/depth_filters.ipynb
#POST PROCESSING https://dev.intelrealsense.com/docs/post-processing-filters 
#VISUAL PRESETS https://dev.intelrealsense.com/docs/d400-series-visual-presets 

def normalize(x):
    return x.astype(float)/255


if __name__=="__main__":
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, COLOR_WIDTH, COLOR_HEIGHT, COLOR_FORMAT, FPS)
    config.enable_stream(rs.stream.depth, DEPTH_WIDTH, DEPTH_HEIGHT, DEPTH_FORMAT, FPS)
    pipeline_cfg = pipeline.start(config)

    depth_sensor = pipeline_cfg.get_device().first_depth_sensor()
    #0 Custorm, 1 Default, 2 Hand, 3 High Accuracy 4 High Density, 5 Medium Density, 6 Remove Ir Pattern
    depth_sensor.set_option(rs.option.visual_preset, 4) 

    for i in range(5):
        if i==0:
            print("Waiting for auto-exposure to settle")
        frames = pipeline.wait_for_frames()
    
    depth_set = []
    for i in range(DEPTH_FRAMES_TO_CAPTURE):
        if i==0: 
            print("Collecting depth set")
        frames = pipeline.wait_for_frames()
        align = rs.align(rs.stream.color)
        aligned_frames = align.process(frames)
        depth_rs = aligned_frames.get_depth_frame()
        depth_set.append(depth_rs)

    
    #depth_rs = aligned_frames.get_depth_frame()
    #filtered_depth_rs = aligned_frames.get_depth_frame
    #depth_map = np.asarray(depth_rs.get_data())

    color_rs = aligned_frames.get_color_frame()
    color_img = np.asarray(color_rs.get_data())
    color_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2RGB)

    decimation_f = rs.decimation_filter()
    threshold_f = rs.threshold_filter(DEPTH_MIN, DEPTH_MAX)
    spatial_f = rs.spatial_filter()
    temporal_f = rs.temporal_filter()
    depth_to_disparity = rs.disparity_transform(True)
    disparity_to_depth = rs.disparity_transform(False)
    
    for depth_rs in depth_set:
        depth_rs = decimation_f.process(depth_rs)
        depth_rs = threshold_f.process(depth_rs)
        depth_rs = depth_to_disparity.process(depth_rs)
        depth_rs = spatial_f.process(depth_rs)
        depth_rs = temporal_f.process(depth_rs)
        depth_rs = disparity_to_depth.process(depth_rs)
    
    #depth_map = np.asarray(depth_rs.get_data())
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

    #Read normalized colors from the color source, in this image color image
    #Colors must be normalized because open3d expects colors values to be floats in range 0 to 1
    color_img_normalized = normalize(color_img)
    pc_colors = color_img_normalized[v, u]

    #Insert colors to the point cloud
    pcd.colors = o3d.utility.Vector3dVector(pc_colors)
    o3d.io.write_point_cloud("test_RGB.ply", pcd)
    o3d.visualization.draw_geometries([pcd])

