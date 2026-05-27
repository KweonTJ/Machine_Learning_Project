from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .common import feature_vector, from_json, now_payload, to_json


class RiskClassifierNode(Node):
    def __init__(self):
        super().__init__("risk_classifier_node")
        self.declare_parameter("features_topic", "/adas/features")
        self.declare_parameter("risk_state_topic", "/adas/risk_state")
        self.declare_parameter("model_path", "")
        self.declare_parameter("brake_ttc_s", 1.2)
        self.declare_parameter("warning_ttc_s", 2.5)
        self.declare_parameter("brake_distance_m", 1.2)
        self.declare_parameter("warning_distance_m", 2.5)
        self.declare_parameter("caution_distance_m", 4.0)

        self.brake_ttc_s = float(self.get_parameter("brake_ttc_s").value)
        self.warning_ttc_s = float(self.get_parameter("warning_ttc_s").value)
        self.brake_distance_m = float(self.get_parameter("brake_distance_m").value)
        self.warning_distance_m = float(
            self.get_parameter("warning_distance_m").value
        )
        self.caution_distance_m = float(
            self.get_parameter("caution_distance_m").value
        )
        self.model = self._load_model()

        self.risk_pub = self.create_publisher(
            String, str(self.get_parameter("risk_state_topic").value), 10
        )
        self.create_subscription(
            String,
            str(self.get_parameter("features_topic").value),
            self.on_features,
            10,
        )
        mode = "RandomForest" if self.model is not None else "rule fallback"
        self.get_logger().info(f"risk classifier ready: {mode}")

    def _load_model(self):
        model_path = str(self.get_parameter("model_path").value).strip()
        if not model_path:
            return None

        path = Path(model_path).expanduser()
        if not path.exists():
            self.get_logger().warn(f"risk model does not exist: {path}")
            return None

        try:
            import joblib

            return joblib.load(path)
        except Exception as exc:  # pragma: no cover - optional dependency
            self.get_logger().error(f"failed to load risk model: {exc}")
            return None

    def on_features(self, msg: String):
        features = from_json(msg.data)
        state = self._predict(features)
        payload = now_payload(risk_state=state, features=features)
        output = String()
        output.data = to_json(payload)
        self.risk_pub.publish(output)

    def _predict(self, features):
        if self.model is not None:
            try:
                return str(self.model.predict([feature_vector(features)])[0])
            except Exception as exc:
                self.get_logger().warn(f"model prediction failed, using rules: {exc}")

        return self._rule_based_state(features)

    def _rule_based_state(self, features):
        if not features.get("person_detected", False):
            return "SAFE"

        z = float(features.get("centroid_z", 99.0))
        ttc = float(features.get("ttc", 99.0))
        overlap = float(features.get("corridor_overlap_ratio", 0.0))
        occlusion = bool(features.get("occlusion_flag", False))

        in_path = overlap >= 0.25
        if in_path and (z <= self.brake_distance_m or ttc <= self.brake_ttc_s):
            return "BRAKE"
        if in_path and (z <= self.warning_distance_m or ttc <= self.warning_ttc_s):
            return "WARNING"
        if in_path or z <= self.caution_distance_m or occlusion:
            return "CAUTION"
        return "SAFE"


def main(args=None):
    rclpy.init(args=args)
    node = RiskClassifierNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
