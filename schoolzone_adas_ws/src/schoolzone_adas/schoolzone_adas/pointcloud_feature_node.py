import math
import time

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image
from std_msgs.msg import String

from .common import empty_features, from_json, now_payload, to_json


class PointCloudFeatureNode(Node):
    def __init__(self):
        super().__init__("pointcloud_feature_node")
        self.declare_parameter("bbox_topic", "/adas/person_bbox")
        self.declare_parameter("depth_topic", "/camera/depth/image_raw")
        self.declare_parameter("camera_info_topic", "/camera/color/camera_info")
        self.declare_parameter("features_topic", "/adas/features")
        self.declare_parameter("min_depth_m", 0.2)
        self.declare_parameter("max_depth_m", 8.0)
        self.declare_parameter("corridor_half_width_m", 0.6)
        self.declare_parameter("corridor_near_m", 0.6)
        self.declare_parameter("corridor_far_m", 4.0)
        self.declare_parameter("bbox_timeout_s", 0.5)

        self.min_depth_m = float(self.get_parameter("min_depth_m").value)
        self.max_depth_m = float(self.get_parameter("max_depth_m").value)
        self.corridor_half_width_m = float(
            self.get_parameter("corridor_half_width_m").value
        )
        self.corridor_near_m = float(self.get_parameter("corridor_near_m").value)
        self.corridor_far_m = float(self.get_parameter("corridor_far_m").value)
        self.bbox_timeout_s = float(self.get_parameter("bbox_timeout_s").value)

        self.bridge = None
        self._load_bridge()

        self.last_bbox = None
        self.last_camera_info = None
        self.previous_detection = False
        self.previous_centroid = None
        self.previous_stamp = None

        self.features_pub = self.create_publisher(
            String, str(self.get_parameter("features_topic").value), 10
        )
        self.create_subscription(
            String, str(self.get_parameter("bbox_topic").value), self.on_bbox, 10
        )
        self.create_subscription(
            CameraInfo,
            str(self.get_parameter("camera_info_topic").value),
            self.on_camera_info,
            10,
        )
        self.create_subscription(
            Image, str(self.get_parameter("depth_topic").value), self.on_depth, 10
        )
        self.get_logger().info("feature extraction node ready")

    def _load_bridge(self):
        try:
            from cv_bridge import CvBridge

            self.bridge = CvBridge()
        except Exception as exc:  # pragma: no cover - depends on ROS install
            self.get_logger().error(f"cv_bridge is not available: {exc}")

    def on_bbox(self, msg: String):
        payload = from_json(msg.data)
        payload["_received_stamp"] = time.time()
        self.last_bbox = payload

    def on_camera_info(self, msg: CameraInfo):
        self.last_camera_info = msg

    def on_depth(self, msg: Image):
        if self.bridge is None:
            return

        bbox = self._current_bbox()
        if not bbox or not bbox.get("person_detected", False):
            self._publish_features(empty_features())
            self.previous_detection = False
            return

        if self.last_camera_info is None:
            self.get_logger().warn("waiting for camera_info")
            return

        try:
            depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        except Exception as exc:
            self.get_logger().warn(f"failed to convert depth image: {exc}")
            return

        features = self._extract(depth, msg.encoding, bbox, self.last_camera_info)
        self._publish_features(features)

    def _current_bbox(self):
        if self.last_bbox is None:
            return None
        age = time.time() - float(self.last_bbox.get("_received_stamp", 0.0))
        if age > self.bbox_timeout_s:
            return None
        return self.last_bbox

    def _depth_meters(self, depth, encoding):
        depth_m = np.asarray(depth, dtype=np.float32)
        if encoding == "16UC1":
            depth_m = depth_m / 1000.0
        return depth_m

    def _extract(self, depth, encoding, bbox_payload, camera_info):
        depth_m = self._depth_meters(depth, encoding)
        height, width = depth_m.shape[:2]
        x1, y1, x2, y2 = [int(v) for v in bbox_payload.get("bbox", [0, 0, 0, 0])]
        x1 = max(0, min(width - 1, x1))
        x2 = max(0, min(width, x2))
        y1 = max(0, min(height - 1, y1))
        y2 = max(0, min(height, y2))

        if x2 <= x1 or y2 <= y1:
            return empty_features()

        roi = depth_m[y1:y2, x1:x2]
        valid = roi[np.isfinite(roi)]
        valid = valid[(valid >= self.min_depth_m) & (valid <= self.max_depth_m)]
        if valid.size == 0:
            return empty_features()

        z = float(np.median(valid))
        fx = float(camera_info.k[0]) if camera_info.k[0] else 1.0
        fy = float(camera_info.k[4]) if camera_info.k[4] else fx
        cx = float(camera_info.k[2])
        cy = float(camera_info.k[5])
        u = 0.5 * (x1 + x2)
        v = 0.5 * (y1 + y2)
        centroid_x = (u - cx) * z / fx
        centroid_y = (v - cy) * z / fy
        extent_x = max((x2 - x1) * z / fx, 0.0)
        extent_y = max((y2 - y1) * z / fy, 0.0)
        overlap_ratio = self._corridor_overlap_ratio(centroid_x, extent_x, z)
        lateral_velocity_x, approach_velocity_z, ttc = self._kinematics(
            centroid_x, z
        )
        occlusion_flag = bool(not self.previous_detection)

        self.previous_detection = True
        self.previous_centroid = (centroid_x, z)
        self.previous_stamp = time.time()

        return {
            "person_detected": True,
            "centroid_x": centroid_x,
            "centroid_y": centroid_y,
            "centroid_z": z,
            "extent_x": extent_x,
            "extent_y": extent_y,
            "corridor_overlap_ratio": overlap_ratio,
            "lateral_velocity_x": lateral_velocity_x,
            "approach_velocity_z": approach_velocity_z,
            "ttc": ttc,
            "occlusion_flag": occlusion_flag,
            "confidence": float(bbox_payload.get("confidence", 0.0)),
        }

    def _corridor_overlap_ratio(self, centroid_x, extent_x, z):
        if z < self.corridor_near_m or z > self.corridor_far_m or extent_x <= 0.0:
            return 0.0
        person_left = centroid_x - 0.5 * extent_x
        person_right = centroid_x + 0.5 * extent_x
        corridor_left = -self.corridor_half_width_m
        corridor_right = self.corridor_half_width_m
        overlap = max(0.0, min(person_right, corridor_right) - max(person_left, corridor_left))
        return float(min(1.0, overlap / extent_x))

    def _kinematics(self, centroid_x, z):
        now = time.time()
        if self.previous_centroid is None or self.previous_stamp is None:
            return 0.0, 0.0, 99.0

        dt = max(now - self.previous_stamp, 1e-3)
        prev_x, prev_z = self.previous_centroid
        lateral_velocity_x = (centroid_x - prev_x) / dt
        approach_velocity_z = (prev_z - z) / dt
        ttc = z / approach_velocity_z if approach_velocity_z > 1e-3 else 99.0
        return float(lateral_velocity_x), float(approach_velocity_z), float(min(ttc, 99.0))

    def _publish_features(self, features):
        payload = now_payload(**features)
        msg = String()
        msg.data = to_json(payload)
        self.features_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = PointCloudFeatureNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
