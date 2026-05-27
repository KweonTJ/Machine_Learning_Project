from glob import glob
import os

from setuptools import find_packages, setup


package_name = "schoolzone_adas"


setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "models"), glob("models/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="student",
    maintainer_email="student@example.com",
    description="School-zone pedestrian ADAS simulator with ROS2, depth features, and machine learning.",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "pedestrian_detector_node = schoolzone_adas.pedestrian_detector_node:main",
            "pointcloud_feature_node = schoolzone_adas.pointcloud_feature_node:main",
            "risk_classifier_node = schoolzone_adas.risk_classifier_node:main",
            "adas_dashboard_node = schoolzone_adas.adas_dashboard_node:main",
            "data_logger_node = schoolzone_adas.data_logger_node:main",
            "train_risk_classifier = schoolzone_adas.train_risk_classifier:main",
        ],
    },
)
