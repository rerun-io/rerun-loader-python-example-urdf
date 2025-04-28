from pathlib import Path
from typing import Optional


def resolve_ros_path(path_str: str) -> str:
    """Resolve a ROS path to an absolute path."""
    if path_str.startswith("package://"):
        path = Path(path_str)
        package_name = path.parts[1]
        relative_path = Path(*path.parts[2:])

        package_path = resolve_ros1_package(package_name) or resolve_ros2_package(package_name)

        if package_path is None:
            raise ValueError(
                f"Could not resolve {path}."
                f"Replace with relative / absolute path, source the correct ROS environment, or install {package_name}."
            )

        return str(package_path / relative_path)
    elif path_str.startswith("file://"):
        return path_str[len("file://") :]
    else:
        return path_str


def resolve_ros2_package(package_name: str) -> Optional[str]:
    try:
        import ament_index_python

        try:
            return ament_index_python.get_package_share_directory(package_name)
        except ament_index_python.packages.PackageNotFoundError:
            return None
    except ImportError:
        return None


def resolve_ros1_package(package_name: str) -> Optional[str]:
    try:
        import rospkg

        try:
            return rospkg.RosPack().get_path(package_name)
        except rospkg.ResourceNotFound:
            return None
    except ImportError:
        return None
