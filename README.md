# Installation
For pi0.5: 
`uv pip install "lerobot[pi]@git+https://github.com/huggingface/lerobot.git"`


# Visualize dataset

`--repo-id felix-newman/pickup_merged \
  --episode-index 0 \
  --root ~/.cache/huggingface/lerobot/felix-newman/pickup_merged`

# Merge Dataset

Merge datasets with local datasets need the absolute path

`lerobot-edit-dataset     --repo_id felix-newman/usb_stick_merged     --operation.type merge     --operation.repo_ids "['/home/felix/.cache/huggingface/lerobot/felix-newman/usb_stick_q1', '/home/felix/.cache/huggingface/lerobot/felix-newman/usb_stick_q2', '/home/felix/.cache/huggingface/lerobot/felix-newman/usb_stick_q3', '/home/felix/.cache/huggingface/lerobot/felix-newman/usb_stick_q4']"`

# Train smolvla

`
lerobot-train \
    --dataset.repo_id=Themistoflix/ginger_80ep \
    --policy.type=smolvla \
    --output_dir=./outputs/smolvla \
    --job_name=smolvla_training \
    --policy.repo_id=Themistoflix/ginger_80ep \
    --policy.pretrained_path=lerobot/smolvla_base \
    --policy.use_amp=true \
    --use_policy_training_preset=false \
    --optimizer.type=adamw \
    --optimizer.lr=5e-5 \
    --optimizer.weight_decay=1e-2 \
    --optimizer.eps=1e-6 \
    --optimizer.betas=[0.9,0.999] \
    --optimizer.grad_clip_norm=1.0 \
    --scheduler.type=cosine_decay_with_warmup \
    --scheduler.num_warmup_steps=1000 \
    --scheduler.num_decay_steps=30000 \
    --scheduler.peak_lr=2.5e-5 \
    --scheduler.decay_lr=2.5e-6 \
    --wandb.enable=true \
    --steps=30000 \
    --save_freq=5000 \
    --policy.device=cuda \
    --batch_size=128`


# Run SmolVLA
`
lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM1 \
  --robot.cameras='{front: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: MJPG}, top: {type: opencv, index_or_path: 2, width: 1280, height: 720, fps: 30, fourcc: MJPG}}' \
  --robot.id=my_awesome_follower_arm \
  --display_data=true \
  --dataset.repo_id=felix-newman/eval_smolvla_ginger \
  --dataset.single_task="Pickup pickup" \
  --dataset.episode_time_s=30 \
  --policy.type=smolvla \
  --policy.pretrained_path=/home/felix/repos/test_robot/outputs/smolvla/checkpoints/025000/pretrained_model
`

# Train pi0
Can definitely go higher on an 80GB GPU - 35GB of memory
`lerobot-train \
    --dataset.repo_id=Themistoflix/ginger_80ep \
    --policy.type=pi0 \
    --output_dir=./outputs/pi0_training \
    --job_name=pi0_training \
    --policy.repo_id=Themistoflix/ginger_80ep \
    --policy.pretrained_path=lerobot/pi0_base \
    --policy.compile_model=false \
    --policy.gradient_checkpointing=true \
    --policy.use_amp=true \
    --use_policy_training_preset=false \
    --optimizer.type=adamw \
    --optimizer.lr=5e-5 \
    --optimizer.weight_decay=1e-2 \
    --optimizer.eps=1e-6 \
    --optimizer.betas=[0.9,0.999] \
    --optimizer.grad_clip_norm=1.0 \
    --scheduler.type=cosine_decay_with_warmup \
    --scheduler.num_warmup_steps=1000 \
    --scheduler.num_decay_steps=30000 \
    --scheduler.peak_lr=2.5e-5 \
    --scheduler.decay_lr=2.5e-6 \
    --wandb.enable=true \
    --policy.dtype=bfloat16 \
    --steps=30000 \
    --save_freq=5000 \
    --policy.device=cuda \
    --batch_size=1
`
# Run pi0
`
`lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM1 \
  --robot.cameras='{front: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: MJPG}, top: {type: opencv, index_or_path: 2, width: 1280, height: 720, fps: 30, fourcc: MJPG}}' \
  --robot.id=my_awesome_follower_arm \
  --display_data=true \
  --dataset.repo_id=felix-newman/eval_pi0_ginger \
  --dataset.single_task="Pickup pickup" \
  --dataset.episode_time_s=30 \
  --dataset.num_episodes=10 \
  --policy.type=pi0 \
  --policy.pretrained_path=/home/felix/repos/test_robot/outputs/pi0/015000/pretrained_model
`


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
