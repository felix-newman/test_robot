from lerobot.datasets import video_utils

from test_robot.patches.video_encoding import fast_encode_video_frames

video_utils.encode_video_frames = fast_encode_video_frames

import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import numpy as np
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig

# Monkey Patch: Speed up image stats computation during recording
from lerobot.datasets import compute_stats
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.processor.factory import make_default_processors
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.scripts.lerobot_record import record_loop
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig
from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import init_rerun
from PIL import Image

_original_sample_images = compute_stats.sample_images
_original_load_image = compute_stats.load_image_as_numpy


def fast_load_image_as_numpy(path, dtype=np.float32, channel_first=False):
    """Faster image loading using PIL directly without extra conversions."""
    img = Image.open(path)
    # Convert to RGB if needed
    if img.mode != "RGB":
        img = img.convert("RGB")
    # Convert to numpy array
    arr = np.array(img, dtype=dtype)
    if channel_first:
        arr = arr.transpose(2, 0, 1)  # HWC -> CHW
    return arr


def fast_sample_images(image_paths: list[str]) -> np.ndarray:
    """Parallel image loading for faster stats computation."""
    from lerobot.datasets.compute_stats import (
        auto_downsample_height_width,
        sample_indices,
    )

    sampled_indices = sample_indices(len(image_paths))

    def load_single_image(idx):
        path = image_paths[idx]
        img = fast_load_image_as_numpy(path, dtype=np.uint8, channel_first=True)
        return auto_downsample_height_width(img)

    # Load images in parallel using thread pool
    with ThreadPoolExecutor(max_workers=8) as executor:
        images_list = list(executor.map(load_single_image, sampled_indices))

    # Stack into single array
    images = np.stack(images_list, axis=0)
    return images


# Apply monkey patches
# compute_stats.sample_images = fast_sample_images
# compute_stats.load_image_as_numpy = fast_load_image_as_numpy


FPS = 30
NUM_EPISODES = 1
EPISODE_TIME_SEC = 60
RESET_TIME_SEC = 3
TASK_DESCRIPTION = "Place box on plate"

from test_robot.config import robot_config, teleop_config

def main():
    print("Starting record dataset...")

    robot = SO101Follower(robot_config)
    teleop = SO101Leader(teleop_config)

    # Configure the dataset features
    action_features = hw_to_dataset_features(robot.action_features, "action")
    obs_features = hw_to_dataset_features(robot.observation_features, "observation")
    dataset_features = {**action_features, **obs_features}

    # Create the dataset
    dataset = LeRobotDataset.create(
        repo_id=f"felix-newman/test-robot-dataset-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        fps=FPS,
        features=dataset_features,
        robot_type=robot.name,
        use_videos=True,
        image_writer_threads=4,
    )

    # Standard Processors. Take the to_transitation and to output functions and apply
    # a noop step in between
    teleop_action_processor, robot_action_processor, robot_observation_processor = (
        make_default_processors()
    )

    # Initialize the keyboard listener and rerun visualization
    _, events = init_keyboard_listener()
    init_rerun(session_name="recording")

    robot.connect(calibrate=False)
    teleop.connect(calibrate=False)

    episode_idx = 0
    while episode_idx < NUM_EPISODES and not events["stop_recording"]:
        try:
            log_say(f"Recording episode {episode_idx + 1} of {NUM_EPISODES}")

            record_loop(
                robot=robot,
                events=events,
                fps=FPS,
                teleop_action_processor=teleop_action_processor,
                robot_action_processor=robot_action_processor,
                robot_observation_processor=robot_observation_processor,
                teleop=teleop,
                dataset=dataset,
                control_time_s=EPISODE_TIME_SEC,
                single_task=TASK_DESCRIPTION,
                display_data=True,
            )

            # Reset the environment if not stopping or re-recording
            if not events["stop_recording"] and (
                episode_idx < NUM_EPISODES - 1 or events["rerecord_episode"]
            ):
                log_say("Reset the environment")
                print("Reset the environment")
                start = time.perf_counter()
                record_loop(
                    robot=robot,
                    events=events,
                    fps=FPS,
                    teleop_action_processor=teleop_action_processor,
                    robot_action_processor=robot_action_processor,
                    robot_observation_processor=robot_observation_processor,
                    teleop=teleop,
                    control_time_s=RESET_TIME_SEC,
                    single_task=TASK_DESCRIPTION,
                    display_data=True,
                )
                end = time.perf_counter()
                print(f"Reset the environment took {end - start:.3f} seconds")

            if events["rerecord_episode"]:
                log_say("Re-recording episode")
                events["rerecord_episode"] = False
                events["exit_early"] = False
                dataset.clear_episode_buffer()
                continue

            print("Saving episode")
            start = time.perf_counter()
            dataset.save_episode()
            end = time.perf_counter()
            print(f"Save episode took {end - start:.3f} seconds")
            episode_idx += 1

            if episode_idx >= NUM_EPISODES:
                break
        except Exception as e:
            print(f"Error recording episode {episode_idx}: {e}")
            traceback.print_exc()
            log_say(
                f"Error recording episode {episode_idx}. Saving dataset and exiting..."
            )
            break

    # Restore the original compute_stats function to compute full stats at the end

    dataset.finalize()

    robot.disconnect()
    teleop.disconnect()


if __name__ == "__main__":
    main()
