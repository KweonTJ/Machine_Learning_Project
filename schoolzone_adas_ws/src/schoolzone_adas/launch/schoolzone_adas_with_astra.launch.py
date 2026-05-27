from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    start_astra = LaunchConfiguration("start_astra")
    use_sim = LaunchConfiguration("use_sim")

    astra_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("astra_camera"), "launch", "astra_mini.launch.py"]
            )
        ),
        launch_arguments={"use_sim": use_sim}.items(),
        condition=IfCondition(start_astra),
    )

    adas_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("schoolzone_adas"),
                    "launch",
                    "schoolzone_adas.launch.py",
                ]
            )
        )
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "start_astra",
                default_value="true",
                description="Launch the Astra Mini camera driver before ADAS nodes.",
            ),
            DeclareLaunchArgument(
                "use_sim",
                default_value="false",
                description="Forwarded to astra_camera/astra_mini.launch.py.",
            ),
            astra_launch,
            adas_launch,
        ]
    )
