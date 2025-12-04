import cv2
import time
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

    T_SECONDS = 3
    start_t = time.perf_counter()
    
    # Capture initial positions once
    start_position = robot.get_observation()
    target_position = teleop_device.get_action()
    
    while True:
        cur_t = time.perf_counter()
        elapsed = cur_t - start_t
        
        if elapsed >= T_SECONDS:
            break

        # Progress from 0 to 1 over T_SECONDS
        alpha = elapsed / T_SECONDS
        
        # Interpolate: start → target
        smoothed_action = {
            k: start_position[k] * (1 - alpha) + target_position[k] * alpha 
            for k in target_position.keys()
        }
        robot.send_action(smoothed_action)

        observation = robot.get_observation()
        cv2.imshow("front", observation["front"][:, :, ::-1])
        cv2.imshow("top", observation["top"][:, :, ::-1])
        if cv2.waitKey(1) == ord("q"):
            break


if __name__ == "__main__":
    main()
