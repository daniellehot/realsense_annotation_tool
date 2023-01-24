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
#https://dev.intelrealsense.com/docs/projection-texture-mapping-and-occlusion-with-intel-realsense-depth-cameras




def create_RGB_pointcloud(points_rs, color):
    v, t = points_rs.get_vertices(), points_rs.get_texture_coordinates()
    verts = np.asanyarray(v).view(np.float32).reshape((-1, 3))
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(verts)
    o3d.io.write_point_cloud("test.ply", pcd)
    #print(verts.shape)  # xyz
    tex_coords = np.asanyarray(t).view(np.float32).reshape((-1, 2))  # uv
    #print(tex_coords.shape)

    cw, ch = color.shape[:2][::-1]
    #print(color.shape[:2])
    #print(color.shape[::-1])
    #print(color.shape[:2][::-1])
    #exit(4)
    v, u = (tex_coords * (cw, ch) + 0.5).astype(np.uint32).T
    np.clip(u, 0, ch-1, out=u)
    np.clip(v, 0, cw-1, out=v)
    #np.savetxt("v.csv", v, delimiter=",")
    #np.savetxt("u.csv", u, delimiter=",")

    print(  color[  [500], u[500]   ]  )
    

def project(v):
    """project 3d vector array to 2d"""
    h, w = out.shape[:2]
    view_aspect = float(h)/w
  
    # ignore divide by zero for invalid depth
    with np.errstate(divide='ignore', invalid='ignore'):
        proj = v[:, :-1] / v[:, -1, np.newaxis] * \
            (w*view_aspect, h) + (w/2.0, h/2.0)
    # near clipping
    znear = 0.03
    proj[v[:, 2] < znear] = np.nan
    return proj


def pointcloud(out, verts, texcoords, color, painter=True):
    """draw point cloud with optional painter's algorithm"""
    proj = project(verts)
    h, w = out.shape[:2]
    j, i = proj.astype(np.uint32).T
    im = (i >= 0) & (i < h)
    jm = (j >= 0) & (j < w)
    m = im & jm
    cw, ch = color.shape[:2][::-1]
    v, u = (texcoords * (cw, ch) + 0.5).astype(np.uint32).T
    np.clip(u, 0, ch-1, out=u)
    np.clip(v, 0, cw-1, out=v)
    out[i[m], j[m]] = color[u[m], v[m]]


def generatePointcloud(depth_frame, color_frame, color_image, maxDistanceMeters = 0.5):
    """ Generate point cloud and update the dynamic point clouds """

    cloud = rs.pointcloud()
    cloud.map_to(color_frame)
    points = rs.points()
    points = cloud.calculate(depth_frame)
    cloud = np.array(np.array(points.get_vertices()).tolist())

    uv = np.array(np.array(points.get_texture_coordinates()).tolist())
    #uv[:,0] = uv[:,0] * 1920
    u = uv[:,0] * 1920
    u_clipped = u [ (0>u) | (1919>u) ]
    print(u.shape)
    print(u_clipped.shape)
    
    #uv[:,1] = uv[:,1] * 1080
    v = uv[:,1] * 1080
    v_clipped = v [ (0>v) | (1079>v) ]
    print(v.shape)
    print(v_clipped.shape)

    uv[:, [1, 0]] = uv[:, [0, 1]]
    uv = np.rint(np.array(uv)).astype(int)

    idx = cloud[:,2] < maxDistanceMeters
    cloud = cloud[idx]
    uv = uv[idx]

    colors = []
    for idx in uv:
        colors.append(color_image[idx[0], idx[1]])
    colors = np.array(colors)
    print(colors.shape)
    print(cloud.shape)

    pcd = o3d.geometry.PointCloud()
    pcd.points[:3] = o3d.utility.Vector3dVector(cloud)
    pcd.points[3:] = o3d.utility.Vector3dVector(colors)




    #cloudColor = colors.flatten()

    #return cloudGeometry, cloudColor, uv

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
    color_source = np.asanyarray(color_rs.get_data())
    generatePointcloud(depth_frame = depth_rs, color_frame = color_rs, color_image = color_source, maxDistanceMeters= 5)
    exit(5)

    pc_rs.map_to(color_rs)
    points_rs = rs.points()
    points_rs = pc_rs.calculate(depth_rs)
    #create_RGB_pointcloud(points_rs, color_img)

    profile = pipeline.get_active_profile()
    depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
    depth_intrinsics = depth_profile.get_intrinsics()
    w, h = depth_intrinsics.width, depth_intrinsics.height
    out = np.empty((h, w, 3), dtype=np.uint8)
    v, t = points_rs.get_vertices(), points_rs.get_texture_coordinates()
    uv_np = np.asanyarray(t)
    print(uv_np)
    exit(5)
    verts = np.asanyarray(v).view(np.float32).reshape((-1, 3))
    texcoords = np.asanyarray(t).view(np.float32).reshape((-1, 2))  # uv
    pointcloud(out, verts, texcoords, color_source)
    print(out.shape)

    print(out.shape)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(verts)
    pcd.color = o3d.utility.Vector3dVector(out)