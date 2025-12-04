from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.robots.so101_follower import SO101FollowerConfig
from lerobot.teleoperators.so101_leader import SO101LeaderConfig


TOP_CAMERA_SCALING = 1.0

camera_config = {
    "front": OpenCVCameraConfig(
        index_or_path=0, width=640, height=480, fps=30, fourcc="MJPG"
    ),
    "top": OpenCVCameraConfig(
        index_or_path=2,
        width=int(1280 * TOP_CAMERA_SCALING),
        height=int(720 * TOP_CAMERA_SCALING),
        fps=30,
        fourcc="MJPG",
    ),
}

robot_config = SO101FollowerConfig(
    port="/dev/ttyACM1", id="my_awesome_follower_arm", cameras=camera_config
)

teleop_config = SO101LeaderConfig(
    port="/dev/ttyACM0",
    id="my_awesome_leader_arm",
)
