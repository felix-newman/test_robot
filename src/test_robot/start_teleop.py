import cv2
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig

from test_robot.config import robot_config, teleop_config


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
