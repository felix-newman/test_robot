# Visualize dataset

`--repo-id felix-newman/pickup_merged \
  --episode-index 0 \
  --root ~/.cache/huggingface/lerobot/felix-newman/pickup_merged`

# Merge Dataset

Merge datasets with local datasets need the absolute path

`lerobot-edit-dataset     --repo_id felix-newman/usb_stick_merged     --operation.type merge     --operation.repo_ids "['/home/felix/.cache/huggingface/lerobot/felix-newman/usb_stick_q1', '/home/felix/.cache/huggingface/lerobot/felix-newman/usb_stick_q2', '/home/felix/.cache/huggingface/lerobot/felix-newman/usb_stick_q3', '/home/felix/.cache/huggingface/lerobot/felix-newman/usb_stick_q4']"`

# Run policy with checkpoint (synchronous)

`lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.cameras='{front: {type: opencv, index_or_path: 4, width: 640, height: 480, fps: 30, fourcc: MJPG}, top: {type: opencv, index_or_path: 6, width: 640, height: 360, fps: 30, fourcc: MJPG}}' \
  --robot.id=my_awesome_follower_arm \
  --display_data=true \
  --dataset.repo_id=felix-newman/eval_pickup12 \
  --dataset.single_task="Pickup pickup" \
  --dataset.episode_time_s=30 \
  --policy.type=act \
  --policy.pretrained_path=/home/felix/repos/test_robot/outputs/train/act_your_dataset/checkpoints/020000/pretrained_model`

# Async inference

python -m lerobot.async_inference.robot_client \
 --server_address=127.0.0.1:8080 \
 --robot.type=so101_follower \
 --robot.port=/dev/ttyACM0 \
 --robot.id=my_awesome_follower_arm \
 --robot.cameras='{ front: {type: opencv, index_or_path: 4, width: 640, height: 480, fps: 30}}' \
 --policy_type=act \
 --pretrained_name_or_path=/home/felix/repos/test_robot/outputs/train/act_so101_test/checkpoints/040000/pretrained_model \
 --policy_device=cuda \
 --actions_per_chunk=50 \
 --chunk_size_threshold=0.5 \
 --aggregate_fn_name=weighted_average \
 --debug_visualize_queue_size=True

# Training
