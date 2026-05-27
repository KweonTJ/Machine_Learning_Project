import csv
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .common import FEATURE_NAMES, from_json


class DataLoggerNode(Node):
    def __init__(self):
        super().__init__("data_logger_node")
        self.declare_parameter("features_topic", "/adas/features")
        self.declare_parameter("risk_state_topic", "/adas/risk_state")
        self.declare_parameter("output_csv", "data/features.csv")

        self.output_csv = Path(str(self.get_parameter("output_csv").value)).expanduser()
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        self.last_features = {}
        self.last_risk = "SAFE"
        self._ensure_header()

        self.create_subscription(
            String, str(self.get_parameter("features_topic").value), self.on_features, 10
        )
        self.create_subscription(
            String,
            str(self.get_parameter("risk_state_topic").value),
            self.on_risk,
            10,
        )
        self.get_logger().info(f"logging features to {self.output_csv}")

    def _ensure_header(self):
        if self.output_csv.exists() and self.output_csv.stat().st_size > 0:
            return
        with self.output_csv.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["stamp", *FEATURE_NAMES, "risk_state"])

    def on_features(self, msg: String):
        self.last_features = from_json(msg.data)
        self._write_row()

    def on_risk(self, msg: String):
        payload = from_json(msg.data)
        self.last_risk = str(payload.get("risk_state", self.last_risk))

    def _write_row(self):
        row = [self.last_features.get("stamp", "")]
        for name in FEATURE_NAMES:
            row.append(self.last_features.get(name, ""))
        row.append(self.last_risk)
        with self.output_csv.open("a", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(row)


def main(args=None):
    rclpy.init(args=args)
    node = DataLoggerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
