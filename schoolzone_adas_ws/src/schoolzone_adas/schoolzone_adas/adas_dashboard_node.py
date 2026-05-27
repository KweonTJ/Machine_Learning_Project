import time

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

from .common import from_json


class AdasDashboardNode(Node):
    def __init__(self):
        super().__init__("adas_dashboard_node")
        self.declare_parameter("image_topic", "/camera/color/image_raw")
        self.declare_parameter("bbox_topic", "/adas/person_bbox")
        self.declare_parameter("features_topic", "/adas/features")
        self.declare_parameter("risk_state_topic", "/adas/risk_state")
        self.declare_parameter("dashboard_image_topic", "/adas/dashboard_image")
        self.declare_parameter("show_window", False)

        self.show_window = bool(self.get_parameter("show_window").value)
        self.bridge = None
        self.cv2 = None
        self._load_cv()

        self.last_bbox = {}
        self.last_features = {}
        self.last_risk = {"risk_state": "SAFE"}
        self.last_frame_time = time.time()
        self.fps = 0.0

        self.dashboard_pub = self.create_publisher(
            Image, str(self.get_parameter("dashboard_image_topic").value), 10
        )
        self.create_subscription(
            String, str(self.get_parameter("bbox_topic").value), self.on_bbox, 10
        )
        self.create_subscription(
            String, str(self.get_parameter("features_topic").value), self.on_features, 10
        )
        self.create_subscription(
            String,
            str(self.get_parameter("risk_state_topic").value),
            self.on_risk,
            10,
        )
        self.create_subscription(
            Image, str(self.get_parameter("image_topic").value), self.on_image, 10
        )
        self.get_logger().info("dashboard node ready")

    def _load_cv(self):
        try:
            import cv2
            from cv_bridge import CvBridge

            self.cv2 = cv2
            self.bridge = CvBridge()
        except Exception as exc:  # pragma: no cover - depends on ROS install
            self.get_logger().error(f"OpenCV/cv_bridge is not available: {exc}")

    def on_bbox(self, msg: String):
        self.last_bbox = from_json(msg.data)

    def on_features(self, msg: String):
        self.last_features = from_json(msg.data)

    def on_risk(self, msg: String):
        self.last_risk = from_json(msg.data, {"risk_state": "SAFE"})

    def on_image(self, msg: Image):
        if self.bridge is None or self.cv2 is None:
            return

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as exc:
            self.get_logger().warn(f"failed to convert dashboard image: {exc}")
            return

        now = time.time()
        dt = max(now - self.last_frame_time, 1e-3)
        self.fps = 0.85 * self.fps + 0.15 * (1.0 / dt)
        self.last_frame_time = now

        dashboard = self._render(frame)
        output = self.bridge.cv2_to_imgmsg(dashboard, encoding="bgr8")
        output.header = msg.header
        self.dashboard_pub.publish(output)

        if self.show_window:
            self.cv2.imshow("School Zone ADAS", dashboard)
            self.cv2.waitKey(1)

    def _render(self, frame):
        cv2 = self.cv2
        canvas = frame.copy()
        height, width = canvas.shape[:2]

        if self.last_bbox.get("person_detected", False):
            x1, y1, x2, y2 = [int(v) for v in self.last_bbox.get("bbox", [0, 0, 0, 0])]
            cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 255, 255), 2)

        side = np.zeros((height, max(320, width // 3), 3), dtype=np.uint8)
        side[:] = (28, 32, 36)
        risk = str(self.last_risk.get("risk_state", "SAFE"))
        color = self._risk_color(risk)

        cv2.putText(side, "School Zone ADAS", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (240, 240, 240), 2)
        cv2.putText(side, risk, (20, 92), cv2.FONT_HERSHEY_SIMPLEX, 1.3, color, 3)
        self._line(side, 140, f"Distance z: {self.last_features.get('centroid_z', 0.0):.2f} m")
        self._line(side, 175, f"Lateral x: {self.last_features.get('centroid_x', 0.0):.2f} m")
        self._line(side, 210, f"TTC: {self.last_features.get('ttc', 99.0):.2f} s")
        self._line(side, 245, f"Corridor: {self.last_features.get('corridor_overlap_ratio', 0.0):.2f}")
        self._line(side, 280, f"FPS: {self.fps:.1f}")
        self._draw_top_view(side)

        return np.hstack([canvas, side])

    def _line(self, image, y, text):
        self.cv2.putText(
            image,
            text,
            (20, y),
            self.cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (220, 220, 220),
            2,
        )

    def _draw_top_view(self, image):
        cv2 = self.cv2
        origin_x = image.shape[1] // 2
        bottom = image.shape[0] - 30
        top = max(320, image.shape[0] - 260)
        cv2.rectangle(image, (origin_x - 55, top), (origin_x + 55, bottom), (80, 80, 80), 2)
        cv2.line(image, (origin_x, bottom), (origin_x, top), (120, 120, 120), 1)

        if not self.last_features.get("person_detected", False):
            return

        x = float(self.last_features.get("centroid_x", 0.0))
        z = float(self.last_features.get("centroid_z", 0.0))
        px = int(origin_x + x * 90.0)
        py = int(bottom - min(max(z, 0.0), 5.0) * 45.0)
        cv2.circle(image, (px, py), 8, self._risk_color(str(self.last_risk.get("risk_state", "SAFE"))), -1)

    def _risk_color(self, risk):
        colors = {
            "SAFE": (80, 210, 120),
            "CAUTION": (0, 210, 255),
            "WARNING": (0, 150, 255),
            "BRAKE": (40, 60, 255),
        }
        return colors.get(risk, (220, 220, 220))


def main(args=None):
    rclpy.init(args=args)
    node = AdasDashboardNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
