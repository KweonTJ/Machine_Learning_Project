from pathlib import Path

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

from .common import now_payload, to_json


class PedestrianDetectorNode(Node):
    def __init__(self):
        super().__init__("pedestrian_detector_node")
        self.declare_parameter("image_topic", "/camera/color/image_raw")
        self.declare_parameter("bbox_topic", "/adas/person_bbox")
        self.declare_parameter("annotated_image_topic", "/adas/detection_image")
        self.declare_parameter("yolo_model_path", "")
        self.declare_parameter("confidence_threshold", 0.35)
        self.declare_parameter("publish_empty_detections", True)

        self.confidence_threshold = float(
            self.get_parameter("confidence_threshold").value
        )
        self.publish_empty = bool(self.get_parameter("publish_empty_detections").value)

        self.bridge = None
        self.model = None
        self.model_ready = False
        self._load_dependencies()

        image_topic = str(self.get_parameter("image_topic").value)
        bbox_topic = str(self.get_parameter("bbox_topic").value)
        annotated_topic = str(self.get_parameter("annotated_image_topic").value)

        self.bbox_pub = self.create_publisher(String, bbox_topic, 10)
        self.annotated_pub = self.create_publisher(Image, annotated_topic, 10)
        self.create_subscription(Image, image_topic, self.on_image, 10)
        self.get_logger().info(f"subscribed image={image_topic}, bbox={bbox_topic}")

    def _load_dependencies(self):
        try:
            from cv_bridge import CvBridge

            self.bridge = CvBridge()
        except Exception as exc:  # pragma: no cover - depends on ROS install
            self.get_logger().error(f"cv_bridge is not available: {exc}")
            return

        model_path = str(self.get_parameter("yolo_model_path").value).strip()
        if not model_path:
            self.get_logger().warn(
                "yolo_model_path is empty. Publishing empty detections until a model is configured."
            )
            return

        path = Path(model_path).expanduser()
        if not path.exists():
            self.get_logger().warn(f"YOLO model does not exist: {path}")
            return

        try:
            from ultralytics import YOLO

            self.model = YOLO(str(path))
            self.model_ready = True
            self.get_logger().info(f"loaded YOLO model: {path}")
        except Exception as exc:  # pragma: no cover - optional ML dependency
            self.get_logger().error(f"failed to load YOLO model: {exc}")

    def on_image(self, msg: Image):
        if self.bridge is None:
            return

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as exc:
            self.get_logger().warn(f"failed to convert image: {exc}")
            return

        if not self.model_ready:
            if self.publish_empty:
                self._publish_detection(False)
            return

        detection = self._detect_person(frame)
        if detection is None:
            self._publish_detection(False)
            return

        x1, y1, x2, y2, confidence = detection
        self._publish_detection(
            True,
            bbox=[int(x1), int(y1), int(x2), int(y2)],
            confidence=float(confidence),
        )
        self._publish_annotated(frame, detection, msg.header)

    def _detect_person(self, frame):
        results = self.model.predict(frame, verbose=False)
        best = None
        best_conf = -1.0
        for result in results:
            names = result.names
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = names.get(class_id, str(class_id))
                confidence = float(box.conf[0])
                if class_name != "person" or confidence < self.confidence_threshold:
                    continue
                if confidence > best_conf:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    best = (x1, y1, x2, y2, confidence)
                    best_conf = confidence
        return best

    def _publish_detection(self, detected, bbox=None, confidence=0.0):
        payload = now_payload(
            person_detected=bool(detected),
            bbox=bbox or [0, 0, 0, 0],
            confidence=float(confidence),
            class_name="person" if detected else "",
        )
        msg = String()
        msg.data = to_json(payload)
        self.bbox_pub.publish(msg)

    def _publish_annotated(self, frame, detection, header):
        try:
            import cv2

            x1, y1, x2, y2, confidence = detection
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 255), 2)
            cv2.putText(
                frame,
                f"person {confidence:.2f}",
                (int(x1), max(20, int(y1) - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )
            image_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            image_msg.header = header
            self.annotated_pub.publish(image_msg)
        except Exception as exc:
            self.get_logger().warn(f"failed to publish annotated image: {exc}")


def main(args=None):
    rclpy.init(args=args)
    node = PedestrianDetectorNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
