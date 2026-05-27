from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    config_file = LaunchConfiguration("config_file")
    default_config = PathJoinSubstitution(
        [FindPackageShare("schoolzone_adas"), "config", "params.yaml"]
    )

    common_args = {
        "package": "schoolzone_adas",
        "output": "screen",
        "parameters": [config_file],
    }

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "config_file",
                default_value=default_config,
                description="Path to the schoolzone ADAS parameter file.",
            ),
            Node(
                **common_args,
                executable="pedestrian_detector_node",
                name="pedestrian_detector_node",
            ),
            Node(
                **common_args,
                executable="pointcloud_feature_node",
                name="pointcloud_feature_node",
            ),
            Node(
                **common_args,
                executable="risk_classifier_node",
                name="risk_classifier_node",
            ),
            Node(
                **common_args,
                executable="adas_dashboard_node",
                name="adas_dashboard_node",
            ),
            Node(
                **common_args,
                executable="data_logger_node",
                name="data_logger_node",
            ),
        ]
    )
