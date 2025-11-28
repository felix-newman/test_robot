import cv2
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig

# camera_config = {
#    "front": OpenCVCameraConfig(
#        index_or_path=4, width=640, height=480, fps=30, fourcc="MJPG"
#    ),
#    "top": OpenCVCameraConfig(
#        index_or_path=8, width=1280, height=720, fps=30, fourcc="MJPG"
#    ),
# }

camera_config = {
    "front": OpenCVCameraConfig(
        index_or_path=4, width=640, height=480, fps=30, fourcc="MJPG"
    ),
    "top": OpenCVCameraConfig(
        index_or_path=6,
        width=int(1280 * 0.5),
        height=int(720 * 0.5),
        fps=30,
        fourcc="MJPG",
    ),
}

robot_config = SO101FollowerConfig(
    port="/dev/ttyACM0", id="my_awesome_follower_arm", cameras=camera_config
)

teleop_config = SO101LeaderConfig(
    port="/dev/ttyACM1",
    id="my_awesome_leader_arm",
)


def main():
    print("Starting teleop...")

    robot = SO101Follower(robot_config)
    teleop_device = SO101Leader(teleop_config)
    robot.connect(calibrate=False)
    teleop_device.connect(calibrate=False)

    while True:
        observation = robot.get_observation()
        action = teleop_device.get_action()
        robot.send_action(action)

        # open cv expects BGR, but observation is RGB
        cv2.imshow("front", observation["front"][:, :, ::-1])
        cv2.imshow("top", observation["top"][:, :, ::-1])
        if cv2.waitKey(1) == ord("q"):
            break


if __name__ == "__main__":
    main()
